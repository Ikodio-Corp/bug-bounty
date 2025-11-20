"""
RBAC API Routes - Role-Based Access Control Endpoints

This module provides REST API endpoints for RBAC management.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...auth.rbac import (
    get_rbac_service,
    RBACService,
    Role,
    Policy,
    PolicyCondition
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/rbac", tags=["RBAC"])


# Request Models
class CreateRoleRequest(BaseModel):
    """Request to create role."""
    id: str = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    description: str = Field(..., description="Role description")
    permissions: List[str] = Field(..., description="Permissions")
    inherits_from: List[str] = Field(default=[], description="Parent roles")


class AssignRoleRequest(BaseModel):
    """Request to assign role."""
    user_id: str = Field(..., description="User ID")
    role_id: str = Field(..., description="Role ID")
    granted_by: str = Field(..., description="Granter ID")
    resource_type: Optional[str] = Field(None, description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource ID")


class CheckAccessRequest(BaseModel):
    """Request to check access."""
    user_id: str = Field(..., description="User ID")
    permission: str = Field(..., description="Permission")
    context: Dict[str, Any] = Field(default={}, description="Context")


class CreatePolicyRequest(BaseModel):
    """Request to create policy."""
    id: str = Field(..., description="Policy ID")
    name: str = Field(..., description="Policy name")
    effect: str = Field(..., description="Effect (allow/deny)")
    permissions: List[str] = Field(..., description="Permissions")
    conditions: List[Dict[str, Any]] = Field(default=[], description="Conditions")
    priority: int = Field(default=0, description="Priority")


# Dependency
async def get_service() -> RBACService:
    """Get RBAC service."""
    return get_rbac_service()


# Role Endpoints
@router.get("/roles", response_model=Dict[str, Any])
async def list_roles(
    service: RBACService = Depends(get_service)
):
    """List all roles."""
    try:
        roles = service.list_roles()

        return {
            "success": True,
            "count": len(roles),
            "roles": [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "permissions_count": len(r.permissions),
                    "inherits_from": r.inherits_from,
                    "is_system": r.is_system
                }
                for r in roles
            ]
        }

    except Exception as e:
        logger.error(f"List roles failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/roles/{role_id}", response_model=Dict[str, Any])
async def get_role(
    role_id: str,
    service: RBACService = Depends(get_service)
):
    """Get role details."""
    try:
        role = service.get_role(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Get all permissions including inherited
        all_permissions = service.get_role_permissions(role_id)

        return {
            "success": True,
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": list(role.permissions),
                "all_permissions": list(all_permissions),
                "inherits_from": role.inherits_from,
                "is_system": role.is_system
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get role failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/roles", response_model=Dict[str, Any])
async def create_role(
    request: CreateRoleRequest,
    service: RBACService = Depends(get_service)
):
    """Create a new role."""
    try:
        role = Role(
            id=request.id,
            name=request.name,
            description=request.description,
            permissions=set(request.permissions),
            inherits_from=request.inherits_from
        )

        created = service.create_role(role)

        return {
            "success": True,
            "message": "Role created",
            "role_id": created.id
        }

    except Exception as e:
        logger.error(f"Create role failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/roles/{role_id}", response_model=Dict[str, Any])
async def delete_role(
    role_id: str,
    service: RBACService = Depends(get_service)
):
    """Delete a role."""
    try:
        success = service.delete_role(role_id)

        if success:
            return {"success": True, "message": "Role deleted"}
        else:
            raise HTTPException(status_code=400, detail="Cannot delete role")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete role failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# User Role Assignment Endpoints
@router.post("/assign", response_model=Dict[str, Any])
async def assign_role(
    request: AssignRoleRequest,
    service: RBACService = Depends(get_service)
):
    """Assign role to user."""
    try:
        assignment = service.assign_role(
            user_id=request.user_id,
            role_id=request.role_id,
            granted_by=request.granted_by,
            resource_type=request.resource_type,
            resource_id=request.resource_id
        )

        return {
            "success": True,
            "message": "Role assigned",
            "user_id": assignment.user_id,
            "role_id": assignment.role_id
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Assign role failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/revoke", response_model=Dict[str, Any])
async def revoke_role(
    user_id: str = Query(..., description="User ID"),
    role_id: str = Query(..., description="Role ID"),
    resource_type: Optional[str] = Query(None, description="Resource type"),
    resource_id: Optional[str] = Query(None, description="Resource ID"),
    service: RBACService = Depends(get_service)
):
    """Revoke role from user."""
    try:
        success = service.revoke_role(
            user_id=user_id,
            role_id=role_id,
            resource_type=resource_type,
            resource_id=resource_id
        )

        if success:
            return {"success": True, "message": "Role revoked"}
        else:
            raise HTTPException(status_code=404, detail="Assignment not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revoke role failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/roles", response_model=Dict[str, Any])
async def get_user_roles(
    user_id: str,
    resource_type: Optional[str] = Query(None, description="Resource type"),
    resource_id: Optional[str] = Query(None, description="Resource ID"),
    service: RBACService = Depends(get_service)
):
    """Get roles assigned to user."""
    try:
        roles = service.get_user_roles(user_id, resource_type, resource_id)

        return {
            "success": True,
            "user_id": user_id,
            "roles": [
                {
                    "role_id": r.role_id,
                    "resource_type": r.resource_type,
                    "resource_id": r.resource_id,
                    "granted_by": r.granted_by,
                    "granted_at": r.granted_at.isoformat()
                }
                for r in roles
            ]
        }

    except Exception as e:
        logger.error(f"Get user roles failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/permissions", response_model=Dict[str, Any])
async def get_user_permissions(
    user_id: str,
    resource_type: Optional[str] = Query(None, description="Resource type"),
    resource_id: Optional[str] = Query(None, description="Resource ID"),
    service: RBACService = Depends(get_service)
):
    """Get all permissions for user."""
    try:
        permissions = service.get_user_permissions(
            user_id, resource_type, resource_id
        )

        return {
            "success": True,
            "user_id": user_id,
            "permissions": list(permissions),
            "count": len(permissions)
        }

    except Exception as e:
        logger.error(f"Get user permissions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Access Check Endpoints
@router.post("/check", response_model=Dict[str, Any])
async def check_access(
    request: CheckAccessRequest,
    service: RBACService = Depends(get_service)
):
    """Check user access."""
    try:
        decision = service.check_access(
            user_id=request.user_id,
            permission=request.permission,
            context=request.context
        )

        return {
            "success": True,
            "allowed": decision.allowed,
            "reason": decision.reason,
            "policy_id": decision.policy_id
        }

    except Exception as e:
        logger.error(f"Check access failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check/{user_id}/{permission}", response_model=Dict[str, Any])
async def has_permission(
    user_id: str,
    permission: str,
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    service: RBACService = Depends(get_service)
):
    """Quick permission check."""
    try:
        allowed = service.has_permission(
            user_id, permission, resource_type, resource_id
        )

        return {
            "success": True,
            "allowed": allowed
        }

    except Exception as e:
        logger.error(f"Has permission check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Policy Endpoints
@router.post("/policies", response_model=Dict[str, Any])
async def create_policy(
    request: CreatePolicyRequest,
    service: RBACService = Depends(get_service)
):
    """Create access policy."""
    try:
        conditions = [
            PolicyCondition(**c) for c in request.conditions
        ]

        policy = Policy(
            id=request.id,
            name=request.name,
            effect=request.effect,
            permissions=request.permissions,
            conditions=conditions,
            priority=request.priority
        )

        created = service.create_policy(policy)

        return {
            "success": True,
            "message": "Policy created",
            "policy_id": created.id
        }

    except Exception as e:
        logger.error(f"Create policy failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/policies/{policy_id}", response_model=Dict[str, Any])
async def delete_policy(
    policy_id: str,
    service: RBACService = Depends(get_service)
):
    """Delete policy."""
    try:
        success = service.delete_policy(policy_id)

        if success:
            return {"success": True, "message": "Policy deleted"}
        else:
            raise HTTPException(status_code=404, detail="Policy not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete policy failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Audit Log Endpoints
@router.get("/audit", response_model=Dict[str, Any])
async def get_audit_log(
    user_id: Optional[str] = Query(None, description="Filter by user"),
    action: Optional[str] = Query(None, description="Filter by action"),
    limit: int = Query(100, description="Max entries"),
    service: RBACService = Depends(get_service)
):
    """Get audit log entries."""
    try:
        logs = service.get_audit_log(user_id, action, limit)

        return {
            "success": True,
            "count": len(logs),
            "entries": logs
        }

    except Exception as e:
        logger.error(f"Get audit log failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/permissions", response_model=Dict[str, Any])
async def list_all_permissions():
    """List all available permissions."""
    from ...auth.rbac import Permission

    return {
        "success": True,
        "permissions": [
            {"id": p.value, "name": p.name}
            for p in Permission
        ]
    }
