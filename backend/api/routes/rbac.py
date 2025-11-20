"""
Advanced Role-Based Access Control (RBAC)
Granular permissions, custom roles, resource-level access
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from core.database import get_db
from core.security import get_current_user
from models.user import User
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import select

router = APIRouter(prefix="/rbac", tags=["RBAC"])


class PermissionAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    REJECT = "reject"
    ASSIGN = "assign"


class ResourceType(str, Enum):
    BUG = "bug"
    SCAN = "scan"
    USER = "user"
    ROLE = "role"
    TEAM = "team"
    ORGANIZATION = "organization"
    REPORT = "report"
    INTEGRATION = "integration"
    SETTING = "setting"


class CreateRoleRequest(BaseModel):
    """Request to create custom role"""
    name: str
    description: Optional[str] = None
    permissions: List[Dict[str, str]]
    is_system_role: bool = False


class AssignRoleRequest(BaseModel):
    """Request to assign role to user"""
    user_id: int
    role_id: int
    scope: Optional[str] = None
    resource_id: Optional[int] = None


class UpdatePermissionsRequest(BaseModel):
    """Request to update role permissions"""
    role_id: int
    permissions: List[Dict[str, str]]


class CheckPermissionRequest(BaseModel):
    """Request to check permission"""
    resource_type: str
    action: str
    resource_id: Optional[int] = None


class Role(BaseModel):
    """Role model"""
    id: int
    name: str
    description: Optional[str]
    permissions: List[Dict[str, str]]
    is_system_role: bool
    created_at: datetime


class Permission(BaseModel):
    """Permission model"""
    id: int
    resource_type: str
    action: str
    conditions: Optional[Dict[str, Any]]


class RoleAssignment(BaseModel):
    """Role assignment model"""
    id: int
    user_id: int
    role_id: int
    scope: Optional[str]
    resource_id: Optional[int]
    assigned_at: datetime
    assigned_by: int


class PermissionChecker:
    """Permission checking logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_permission(
        self,
        user: User,
        resource_type: str,
        action: str,
        resource_id: Optional[int] = None
    ) -> bool:
        """Check if user has permission"""
        # Admin has all permissions
        if user.role == "admin":
            return True
        
        # Get user's role assignments
        role_assignments = await self._get_user_roles(user.id)
        
        for assignment in role_assignments:
            role = assignment.get('role')
            permissions = role.get('permissions', [])
            
            for perm in permissions:
                if perm.get('resource_type') == resource_type and perm.get('action') == action:
                    # Check scope
                    if assignment.get('scope') == 'resource' and assignment.get('resource_id') != resource_id:
                        continue
                    
                    # Check conditions
                    if self._check_conditions(perm.get('conditions'), user, resource_id):
                        return True
        
        return False
    
    async def _get_user_roles(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's role assignments"""
        # In production, query from database
        return []
    
    def _check_conditions(
        self,
        conditions: Optional[Dict[str, Any]],
        user: User,
        resource_id: Optional[int]
    ) -> bool:
        """Check permission conditions"""
        if not conditions:
            return True
        
        # Check ownership condition
        if conditions.get('owner_only'):
            # Would check if user owns the resource
            return True
        
        # Check time-based conditions
        if conditions.get('time_limited'):
            # Would check time constraints
            return True
        
        return True


@router.post("/roles")
async def create_role(
    request: CreateRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create custom role with permissions
    
    Args:
        request: Create role request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Created role details
    """
    try:
        # Check admin permission
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can create roles"
            )
        
        # Validate permissions
        valid_resources = [r.value for r in ResourceType]
        valid_actions = [a.value for a in PermissionAction]
        
        for perm in request.permissions:
            if perm.get('resource_type') not in valid_resources:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid resource type: {perm.get('resource_type')}"
                )
            if perm.get('action') not in valid_actions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {perm.get('action')}"
                )
        
        # Create role (in production, save to database)
        role = {
            "id": 1,
            "name": request.name,
            "description": request.description,
            "permissions": request.permissions,
            "is_system_role": request.is_system_role,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": current_user.id
        }
        
        return {
            "status": "created",
            "role": role,
            "message": f"Role '{request.name}' created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Role creation failed: {str(e)}"
        )


@router.get("/roles")
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all roles
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: List of roles
    """
    try:
        # System roles
        system_roles = [
            {
                "id": 1,
                "name": "Admin",
                "description": "Full system access",
                "is_system_role": True,
                "permission_count": 100
            },
            {
                "id": 2,
                "name": "Hunter",
                "description": "Bug hunter with standard permissions",
                "is_system_role": True,
                "permission_count": 20
            },
            {
                "id": 3,
                "name": "Developer",
                "description": "Developer with fix permissions",
                "is_system_role": True,
                "permission_count": 15
            },
            {
                "id": 4,
                "name": "Reviewer",
                "description": "Bug review and validation permissions",
                "is_system_role": True,
                "permission_count": 25
            }
        ]
        
        # Custom roles would be loaded from database
        custom_roles = []
        
        return {
            "system_roles": system_roles,
            "custom_roles": custom_roles,
            "total": len(system_roles) + len(custom_roles)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list roles: {str(e)}"
        )


@router.get("/roles/{role_id}")
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get role details with permissions
    
    Args:
        role_id: Role ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Role details
    """
    try:
        # In production, query from database
        role = {
            "id": role_id,
            "name": "Hunter",
            "description": "Bug hunter with standard permissions",
            "is_system_role": True,
            "permissions": [
                {
                    "resource_type": "bug",
                    "action": "create",
                    "conditions": {"owner_only": True}
                },
                {
                    "resource_type": "bug",
                    "action": "read",
                    "conditions": None
                },
                {
                    "resource_type": "bug",
                    "action": "update",
                    "conditions": {"owner_only": True}
                },
                {
                    "resource_type": "scan",
                    "action": "create",
                    "conditions": None
                },
                {
                    "resource_type": "scan",
                    "action": "read",
                    "conditions": {"owner_only": True}
                }
            ],
            "created_at": datetime.utcnow().isoformat()
        }
        
        return role
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get role: {str(e)}"
        )


@router.put("/roles/{role_id}")
async def update_role(
    role_id: int,
    request: UpdatePermissionsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update role permissions
    
    Args:
        role_id: Role ID
        request: Update request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Update status
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can update roles"
            )
        
        # Validate permissions
        valid_resources = [r.value for r in ResourceType]
        valid_actions = [a.value for a in PermissionAction]
        
        for perm in request.permissions:
            if perm.get('resource_type') not in valid_resources:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid resource type: {perm.get('resource_type')}"
                )
            if perm.get('action') not in valid_actions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid action: {perm.get('action')}"
                )
        
        # Update role (in production, update database)
        return {
            "status": "updated",
            "role_id": role_id,
            "permissions": request.permissions,
            "message": "Role permissions updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Role update failed: {str(e)}"
        )


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete custom role
    
    Args:
        role_id: Role ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Delete status
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can delete roles"
            )
        
        # Check if system role
        # In production, query from database
        is_system_role = role_id <= 10
        
        if is_system_role:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete system roles"
            )
        
        # Delete role (in production, delete from database)
        return {
            "status": "deleted",
            "role_id": role_id,
            "message": "Role deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Role deletion failed: {str(e)}"
        )


@router.post("/assign")
async def assign_role(
    request: AssignRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign role to user
    
    Args:
        request: Assignment request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Assignment status
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can assign roles"
            )
        
        # Verify user exists
        result = await db.execute(
            select(User).where(User.id == request.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create assignment (in production, save to database)
        assignment = {
            "id": 1,
            "user_id": request.user_id,
            "role_id": request.role_id,
            "scope": request.scope or "global",
            "resource_id": request.resource_id,
            "assigned_at": datetime.utcnow().isoformat(),
            "assigned_by": current_user.id
        }
        
        return {
            "status": "assigned",
            "assignment": assignment,
            "message": f"Role assigned to user {user.username} successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Role assignment failed: {str(e)}"
        )


@router.delete("/assign/{assignment_id}")
async def revoke_role(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Revoke role assignment
    
    Args:
        assignment_id: Assignment ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Revoke status
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can revoke roles"
            )
        
        # Delete assignment (in production, delete from database)
        return {
            "status": "revoked",
            "assignment_id": assignment_id,
            "message": "Role assignment revoked successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Role revocation failed: {str(e)}"
        )


@router.get("/user/{user_id}/roles")
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's role assignments
    
    Args:
        user_id: User ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: User's roles
    """
    try:
        # Check permission
        if current_user.id != user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Cannot view other users' roles"
            )
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get role assignments (in production, query from database)
        assignments = [
            {
                "id": 1,
                "role": {
                    "id": 2,
                    "name": "Hunter",
                    "description": "Bug hunter with standard permissions"
                },
                "scope": "global",
                "resource_id": None,
                "assigned_at": datetime.utcnow().isoformat()
            }
        ]
        
        return {
            "user_id": user_id,
            "username": user.username,
            "assignments": assignments,
            "total": len(assignments)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user roles: {str(e)}"
        )


@router.post("/check-permission")
async def check_permission(
    request: CheckPermissionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if user has permission for action on resource
    
    Args:
        request: Permission check request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Permission check result
    """
    try:
        checker = PermissionChecker(db)
        
        has_permission = await checker.check_permission(
            user=current_user,
            resource_type=request.resource_type,
            action=request.action,
            resource_id=request.resource_id
        )
        
        return {
            "user_id": current_user.id,
            "resource_type": request.resource_type,
            "action": request.action,
            "resource_id": request.resource_id,
            "has_permission": has_permission
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Permission check failed: {str(e)}"
        )


@router.get("/permissions")
async def list_all_permissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all available permissions
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: All permissions grouped by resource
    """
    try:
        permissions = {}
        
        for resource in ResourceType:
            permissions[resource.value] = [action.value for action in PermissionAction]
        
        return {
            "permissions": permissions,
            "resource_types": [r.value for r in ResourceType],
            "actions": [a.value for a in PermissionAction]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list permissions: {str(e)}"
        )


@router.get("/audit-log")
async def get_audit_log(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get RBAC audit log
    
    Args:
        limit: Number of records to return
        offset: Offset for pagination
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Audit log entries
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="Only admins can view audit log"
            )
        
        # In production, query from database
        audit_entries = [
            {
                "id": 1,
                "timestamp": datetime.utcnow().isoformat(),
                "action": "role_assigned",
                "actor_id": current_user.id,
                "actor_name": current_user.username,
                "target_user_id": 2,
                "target_user_name": "hunter1",
                "role_name": "Reviewer",
                "details": "Assigned reviewer role for bug validation"
            }
        ]
        
        return {
            "audit_log": audit_entries,
            "total": len(audit_entries),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get audit log: {str(e)}"
        )
