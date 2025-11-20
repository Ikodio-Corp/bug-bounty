"""
Auth Package - Authentication and Authorization

This package provides comprehensive authentication and authorization
including OAuth2, MFA, and RBAC.
"""

from .oauth_providers import (
    OAuthService,
    OAuthProvider,
    OAuthConfig,
    OAuthUserInfo,
    SAMLService,
    SAMLConfig,
    get_oauth_service,
    get_saml_service
)
from .mfa import (
    MFAService,
    MFAMethod,
    MFASetup,
    MFAVerification,
    TOTPService,
    BackupCodesService,
    get_mfa_service
)
from .rbac import (
    RBACService,
    Permission,
    Role,
    UserRole,
    Policy,
    PolicyCondition,
    AccessDecision,
    get_rbac_service
)

__all__ = [
    # OAuth
    "OAuthService",
    "OAuthProvider",
    "OAuthConfig",
    "OAuthUserInfo",
    "SAMLService",
    "SAMLConfig",
    "get_oauth_service",
    "get_saml_service",
    # MFA
    "MFAService",
    "MFAMethod",
    "MFASetup",
    "MFAVerification",
    "TOTPService",
    "BackupCodesService",
    "get_mfa_service",
    # RBAC
    "RBACService",
    "Permission",
    "Role",
    "UserRole",
    "Policy",
    "PolicyCondition",
    "AccessDecision",
    "get_rbac_service"
]
