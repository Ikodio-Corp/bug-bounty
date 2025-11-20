"""
Advanced RBAC System - Role-Based Access Control Implementation

This module provides comprehensive RBAC with:
- Hierarchical roles
- Fine-grained permissions
- Resource-based access control
- Dynamic policy evaluation
- Audit logging
"""

import logging
from typing import Any, Dict, List, Optional, Set
from enum import Enum
from datetime import datetime

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """System permissions."""
    # Scan permissions
    SCAN_CREATE = "scan:create"
    SCAN_READ = "scan:read"
    SCAN_UPDATE = "scan:update"
    SCAN_DELETE = "scan:delete"
    SCAN_EXECUTE = "scan:execute"

    # Vulnerability permissions
    VULN_READ = "vulnerability:read"
    VULN_UPDATE = "vulnerability:update"
    VULN_VERIFY = "vulnerability:verify"
    VULN_EXPORT = "vulnerability:export"

    # Bug report permissions
    BUG_CREATE = "bug:create"
    BUG_READ = "bug:read"
    BUG_UPDATE = "bug:update"
    BUG_DELETE = "bug:delete"
    BUG_ASSIGN = "bug:assign"
    BUG_TRIAGE = "bug:triage"
    BUG_CLOSE = "bug:close"

    # Payment permissions
    PAYMENT_VIEW = "payment:view"
    PAYMENT_CREATE = "payment:create"
    PAYMENT_APPROVE = "payment:approve"
    PAYMENT_REFUND = "payment:refund"

    # User permissions
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_SUSPEND = "user:suspend"

    # Team permissions
    TEAM_CREATE = "team:create"
    TEAM_READ = "team:read"
    TEAM_UPDATE = "team:update"
    TEAM_DELETE = "team:delete"
    TEAM_INVITE = "team:invite"

    # Organization permissions
    ORG_READ = "organization:read"
    ORG_UPDATE = "organization:update"
    ORG_BILLING = "organization:billing"
    ORG_SETTINGS = "organization:settings"

    # Program permissions
    PROGRAM_CREATE = "program:create"
    PROGRAM_READ = "program:read"
    PROGRAM_UPDATE = "program:update"
    PROGRAM_DELETE = "program:delete"
    PROGRAM_PUBLISH = "program:publish"

    # Admin permissions
    ADMIN_FULL = "admin:full"
    ADMIN_AUDIT = "admin:audit"
    ADMIN_CONFIG = "admin:config"

    # API permissions
    API_KEY_CREATE = "api_key:create"
    API_KEY_READ = "api_key:read"
    API_KEY_REVOKE = "api_key:revoke"


class Role(BaseModel):
    """Role definition."""
    id: str
    name: str
    description: str
    permissions: Set[str]
    inherits_from: List[str] = []
    is_system: bool = False
    created_at: datetime = datetime.utcnow()


class UserRole(BaseModel):
    """User role assignment."""
    user_id: str
    role_id: str
    resource_type: Optional[str] = None  # org, team, program
    resource_id: Optional[str] = None
    granted_by: str
    granted_at: datetime = datetime.utcnow()
    expires_at: Optional[datetime] = None


class PolicyCondition(BaseModel):
    """Policy condition for dynamic evaluation."""
    field: str
    operator: str  # eq, ne, gt, lt, in, contains
    value: Any


class Policy(BaseModel):
    """Access policy."""
    id: str
    name: str
    effect: str  # allow, deny
    permissions: List[str]
    conditions: List[PolicyCondition] = []
    priority: int = 0


class AccessDecision(BaseModel):
    """Access decision result."""
    allowed: bool
    reason: str
    policy_id: Optional[str] = None
    evaluated_at: datetime = datetime.utcnow()


class RBACService:
    """
    Advanced RBAC Service.

    Provides:
    - Role management
    - Permission evaluation
    - Policy-based access control
    - Resource-level permissions
    - Audit logging
    """

    def __init__(self):
        """Initialize RBAC service."""
        self._roles: Dict[str, Role] = {}
        self._user_roles: Dict[str, List[UserRole]] = {}
        self._policies: Dict[str, Policy] = {}
        self._audit_log: List[Dict[str, Any]] = []

        # Initialize default roles
        self._init_default_roles()

    def _init_default_roles(self) -> None:
        """Initialize default system roles."""
        # Guest role
        self.create_role(Role(
            id="guest",
            name="Guest",
            description="Limited read-only access",
            permissions={
                Permission.SCAN_READ.value,
                Permission.VULN_READ.value,
                Permission.PROGRAM_READ.value
            },
            is_system=True
        ))

        # Researcher role
        self.create_role(Role(
            id="researcher",
            name="Researcher",
            description="Bug bounty researcher",
            permissions={
                Permission.BUG_CREATE.value,
                Permission.BUG_READ.value,
                Permission.BUG_UPDATE.value,
                Permission.PAYMENT_VIEW.value
            },
            inherits_from=["guest"],
            is_system=True
        ))

        # Triager role
        self.create_role(Role(
            id="triager",
            name="Triager",
            description="Bug triage and initial review",
            permissions={
                Permission.BUG_TRIAGE.value,
                Permission.BUG_ASSIGN.value,
                Permission.VULN_VERIFY.value
            },
            inherits_from=["researcher"],
            is_system=True
        ))

        # Analyst role
        self.create_role(Role(
            id="analyst",
            name="Security Analyst",
            description="Security analysis and scanning",
            permissions={
                Permission.SCAN_CREATE.value,
                Permission.SCAN_EXECUTE.value,
                Permission.VULN_UPDATE.value,
                Permission.VULN_EXPORT.value,
                Permission.BUG_CLOSE.value
            },
            inherits_from=["triager"],
            is_system=True
        ))

        # Team Lead role
        self.create_role(Role(
            id="team_lead",
            name="Team Lead",
            description="Team management",
            permissions={
                Permission.TEAM_CREATE.value,
                Permission.TEAM_UPDATE.value,
                Permission.TEAM_INVITE.value,
                Permission.USER_READ.value,
                Permission.PAYMENT_CREATE.value
            },
            inherits_from=["analyst"],
            is_system=True
        ))

        # Program Manager role
        self.create_role(Role(
            id="program_manager",
            name="Program Manager",
            description="Bug bounty program management",
            permissions={
                Permission.PROGRAM_CREATE.value,
                Permission.PROGRAM_UPDATE.value,
                Permission.PROGRAM_PUBLISH.value,
                Permission.PAYMENT_APPROVE.value
            },
            inherits_from=["team_lead"],
            is_system=True
        ))

        # Organization Admin role
        self.create_role(Role(
            id="org_admin",
            name="Organization Admin",
            description="Organization administration",
            permissions={
                Permission.ORG_UPDATE.value,
                Permission.ORG_BILLING.value,
                Permission.ORG_SETTINGS.value,
                Permission.USER_CREATE.value,
                Permission.USER_UPDATE.value,
                Permission.USER_SUSPEND.value,
                Permission.TEAM_DELETE.value,
                Permission.PROGRAM_DELETE.value,
                Permission.API_KEY_CREATE.value,
                Permission.API_KEY_READ.value,
                Permission.API_KEY_REVOKE.value
            },
            inherits_from=["program_manager"],
            is_system=True
        ))

        # Super Admin role
        self.create_role(Role(
            id="super_admin",
            name="Super Admin",
            description="Full system access",
            permissions={
                Permission.ADMIN_FULL.value,
                Permission.ADMIN_AUDIT.value,
                Permission.ADMIN_CONFIG.value,
                Permission.USER_DELETE.value,
                Permission.PAYMENT_REFUND.value,
                Permission.SCAN_DELETE.value,
                Permission.BUG_DELETE.value
            },
            inherits_from=["org_admin"],
            is_system=True
        ))

    def create_role(self, role: Role) -> Role:
        """Create a new role."""
        self._roles[role.id] = role
        logger.info(f"Created role: {role.id}")
        return role

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self._roles.get(role_id)

    def update_role(self, role_id: str, updates: Dict[str, Any]) -> Optional[Role]:
        """Update role."""
        if role_id not in self._roles:
            return None

        role = self._roles[role_id]
        if role.is_system and "permissions" in updates:
            logger.warning(f"Cannot modify permissions of system role: {role_id}")
            return None

        for key, value in updates.items():
            if hasattr(role, key):
                setattr(role, key, value)

        return role

    def delete_role(self, role_id: str) -> bool:
        """Delete role."""
        if role_id not in self._roles:
            return False

        if self._roles[role_id].is_system:
            logger.warning(f"Cannot delete system role: {role_id}")
            return False

        del self._roles[role_id]
        return True

    def get_role_permissions(self, role_id: str) -> Set[str]:
        """
        Get all permissions for a role including inherited.

        Args:
            role_id: Role ID

        Returns:
            Set of permission strings
        """
        if role_id not in self._roles:
            return set()

        role = self._roles[role_id]
        permissions = set(role.permissions)

        # Add inherited permissions
        for parent_id in role.inherits_from:
            permissions.update(self.get_role_permissions(parent_id))

        return permissions

    def assign_role(
        self,
        user_id: str,
        role_id: str,
        granted_by: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """
        Assign role to user.

        Args:
            user_id: User ID
            role_id: Role ID to assign
            granted_by: ID of user granting the role
            resource_type: Optional resource scope (org, team, program)
            resource_id: Optional resource ID
            expires_at: Optional expiration

        Returns:
            UserRole assignment
        """
        if role_id not in self._roles:
            raise ValueError(f"Role {role_id} not found")

        assignment = UserRole(
            user_id=user_id,
            role_id=role_id,
            resource_type=resource_type,
            resource_id=resource_id,
            granted_by=granted_by,
            expires_at=expires_at
        )

        if user_id not in self._user_roles:
            self._user_roles[user_id] = []

        self._user_roles[user_id].append(assignment)

        self._log_audit(
            action="role_assigned",
            user_id=user_id,
            details={
                "role_id": role_id,
                "granted_by": granted_by,
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

        return assignment

    def revoke_role(
        self,
        user_id: str,
        role_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> bool:
        """Revoke role from user."""
        if user_id not in self._user_roles:
            return False

        original_count = len(self._user_roles[user_id])
        self._user_roles[user_id] = [
            r for r in self._user_roles[user_id]
            if not (
                r.role_id == role_id and
                r.resource_type == resource_type and
                r.resource_id == resource_id
            )
        ]

        if len(self._user_roles[user_id]) < original_count:
            self._log_audit(
                action="role_revoked",
                user_id=user_id,
                details={
                    "role_id": role_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id
                }
            )
            return True

        return False

    def get_user_roles(
        self,
        user_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> List[UserRole]:
        """Get roles for a user."""
        if user_id not in self._user_roles:
            return []

        roles = self._user_roles[user_id]
        now = datetime.utcnow()

        # Filter expired roles
        roles = [r for r in roles if not r.expires_at or r.expires_at > now]

        # Filter by resource if specified
        if resource_type:
            roles = [
                r for r in roles
                if r.resource_type is None or (
                    r.resource_type == resource_type and
                    (resource_id is None or r.resource_id == resource_id)
                )
            ]

        return roles

    def get_user_permissions(
        self,
        user_id: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> Set[str]:
        """Get all permissions for a user."""
        roles = self.get_user_roles(user_id, resource_type, resource_id)
        permissions = set()

        for user_role in roles:
            permissions.update(self.get_role_permissions(user_role.role_id))

        return permissions

    def has_permission(
        self,
        user_id: str,
        permission: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Check if user has permission.

        Args:
            user_id: User ID
            permission: Permission to check
            resource_type: Optional resource scope
            resource_id: Optional resource ID

        Returns:
            True if user has permission
        """
        permissions = self.get_user_permissions(user_id, resource_type, resource_id)

        # Check for admin full access
        if Permission.ADMIN_FULL.value in permissions:
            return True

        return permission in permissions

    def check_access(
        self,
        user_id: str,
        permission: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AccessDecision:
        """
        Check access with policy evaluation.

        Args:
            user_id: User ID
            permission: Permission to check
            context: Optional context for policy evaluation

        Returns:
            AccessDecision with result and reason
        """
        context = context or {}
        resource_type = context.get("resource_type")
        resource_id = context.get("resource_id")

        # Check basic permission
        if not self.has_permission(user_id, permission, resource_type, resource_id):
            decision = AccessDecision(
                allowed=False,
                reason="Permission not granted"
            )
            self._log_access(user_id, permission, decision, context)
            return decision

        # Evaluate policies
        for policy in sorted(self._policies.values(), key=lambda p: -p.priority):
            if permission in policy.permissions:
                if self._evaluate_conditions(policy.conditions, context):
                    allowed = policy.effect == "allow"
                    decision = AccessDecision(
                        allowed=allowed,
                        reason=f"Policy {policy.name} {'allowed' if allowed else 'denied'}",
                        policy_id=policy.id
                    )
                    self._log_access(user_id, permission, decision, context)
                    return decision

        # Default allow if permission granted
        decision = AccessDecision(
            allowed=True,
            reason="Permission granted"
        )
        self._log_access(user_id, permission, decision, context)
        return decision

    def _evaluate_conditions(
        self,
        conditions: List[PolicyCondition],
        context: Dict[str, Any]
    ) -> bool:
        """Evaluate policy conditions."""
        for condition in conditions:
            value = context.get(condition.field)

            if condition.operator == "eq":
                if value != condition.value:
                    return False
            elif condition.operator == "ne":
                if value == condition.value:
                    return False
            elif condition.operator == "gt":
                if not value or value <= condition.value:
                    return False
            elif condition.operator == "lt":
                if not value or value >= condition.value:
                    return False
            elif condition.operator == "in":
                if value not in condition.value:
                    return False
            elif condition.operator == "contains":
                if condition.value not in (value or []):
                    return False

        return True

    def create_policy(self, policy: Policy) -> Policy:
        """Create access policy."""
        self._policies[policy.id] = policy
        logger.info(f"Created policy: {policy.id}")
        return policy

    def delete_policy(self, policy_id: str) -> bool:
        """Delete policy."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False

    def _log_audit(
        self,
        action: str,
        user_id: str,
        details: Dict[str, Any]
    ) -> None:
        """Log audit event."""
        self._audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details
        })

    def _log_access(
        self,
        user_id: str,
        permission: str,
        decision: AccessDecision,
        context: Dict[str, Any]
    ) -> None:
        """Log access check."""
        self._audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "access_check",
            "user_id": user_id,
            "permission": permission,
            "allowed": decision.allowed,
            "reason": decision.reason,
            "context": context
        })

    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        logs = self._audit_log

        if user_id:
            logs = [l for l in logs if l.get("user_id") == user_id]
        if action:
            logs = [l for l in logs if l.get("action") == action]

        return logs[-limit:]

    def list_roles(self) -> List[Role]:
        """List all roles."""
        return list(self._roles.values())


# Singleton instance
_rbac_service: Optional[RBACService] = None


def get_rbac_service() -> RBACService:
    """Get the global RBAC service instance."""
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service


__all__ = [
    "RBACService",
    "Permission",
    "Role",
    "UserRole",
    "Policy",
    "PolicyCondition",
    "AccessDecision",
    "get_rbac_service"
]
