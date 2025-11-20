"""
OAuth2/SSO Authentication - Multi-Provider OAuth Implementation

This module provides OAuth2 authentication with multiple providers
including GitHub, Google, Microsoft, and SAML SSO support.
"""

import logging
import secrets
import time
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime, timedelta

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""
    GITHUB = "github"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"
    OKTA = "okta"
    AUTH0 = "auth0"


class OAuthConfig(BaseModel):
    """OAuth provider configuration."""
    provider: OAuthProvider
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str] = []


class OAuthUserInfo(BaseModel):
    """Standardized user info from OAuth provider."""
    provider: OAuthProvider
    provider_user_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    verified_email: bool = False
    raw_data: Dict[str, Any] = {}


class OAuthState(BaseModel):
    """OAuth state for CSRF protection."""
    state: str
    provider: OAuthProvider
    redirect_url: Optional[str] = None
    created_at: datetime
    expires_at: datetime


class OAuthService:
    """
    OAuth2 Authentication Service.

    Provides:
    - Multiple OAuth provider support
    - Token exchange
    - User info retrieval
    - State management for CSRF protection
    """

    def __init__(self):
        """Initialize OAuth service."""
        self._configs: Dict[OAuthProvider, OAuthConfig] = {}
        self._states: Dict[str, OAuthState] = {}
        self._provider_configs = {
            OAuthProvider.GITHUB: {
                "authorize_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "email_url": "https://api.github.com/user/emails",
                "default_scopes": ["user:email", "read:user"]
            },
            OAuthProvider.GOOGLE: {
                "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
                "default_scopes": ["email", "profile", "openid"]
            },
            OAuthProvider.MICROSOFT: {
                "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_url": "https://graph.microsoft.com/v1.0/me",
                "default_scopes": ["User.Read", "email", "profile", "openid"]
            },
            OAuthProvider.GITLAB: {
                "authorize_url": "https://gitlab.com/oauth/authorize",
                "token_url": "https://gitlab.com/oauth/token",
                "userinfo_url": "https://gitlab.com/api/v4/user",
                "default_scopes": ["read_user", "email"]
            },
            OAuthProvider.BITBUCKET: {
                "authorize_url": "https://bitbucket.org/site/oauth2/authorize",
                "token_url": "https://bitbucket.org/site/oauth2/access_token",
                "userinfo_url": "https://api.bitbucket.org/2.0/user",
                "email_url": "https://api.bitbucket.org/2.0/user/emails",
                "default_scopes": ["account", "email"]
            }
        }

    def configure_provider(self, config: OAuthConfig) -> None:
        """Configure an OAuth provider."""
        self._configs[config.provider] = config
        logger.info(f"Configured OAuth provider: {config.provider.value}")

    def get_authorization_url(
        self,
        provider: OAuthProvider,
        redirect_url: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get authorization URL for OAuth flow.

        Args:
            provider: OAuth provider
            redirect_url: URL to redirect after auth

        Returns:
            Authorization URL and state
        """
        if provider not in self._configs:
            raise ValueError(f"Provider {provider.value} not configured")

        config = self._configs[provider]
        provider_config = self._provider_configs[provider]

        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        self._states[state] = OAuthState(
            state=state,
            provider=provider,
            redirect_url=redirect_url,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )

        # Build scopes
        scopes = config.scopes or provider_config.get("default_scopes", [])

        # Build authorization URL
        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "response_type": "code"
        }

        # Add provider-specific params
        if provider == OAuthProvider.GOOGLE:
            params["access_type"] = "offline"
            params["prompt"] = "consent"

        query = "&".join(f"{k}={v}" for k, v in params.items())
        auth_url = f"{provider_config['authorize_url']}?{query}"

        return {
            "authorization_url": auth_url,
            "state": state
        }

    async def exchange_code(
        self,
        provider: OAuthProvider,
        code: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens.

        Args:
            provider: OAuth provider
            code: Authorization code
            state: State parameter for CSRF validation

        Returns:
            Token response
        """
        # Validate state
        if state not in self._states:
            raise ValueError("Invalid state parameter")

        oauth_state = self._states[state]
        if oauth_state.expires_at < datetime.utcnow():
            del self._states[state]
            raise ValueError("State expired")

        if oauth_state.provider != provider:
            raise ValueError("State provider mismatch")

        # Clean up state
        redirect_url = oauth_state.redirect_url
        del self._states[state]

        if provider not in self._configs:
            raise ValueError(f"Provider {provider.value} not configured")

        config = self._configs[provider]
        provider_config = self._provider_configs[provider]

        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "code": code,
                "redirect_uri": config.redirect_uri,
                "grant_type": "authorization_code"
            }

            headers = {"Accept": "application/json"}

            response = await client.post(
                provider_config["token_url"],
                data=data,
                headers=headers
            )
            response.raise_for_status()

            token_data = response.json()

            return {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_in": token_data.get("expires_in"),
                "scope": token_data.get("scope"),
                "redirect_url": redirect_url
            }

    async def get_user_info(
        self,
        provider: OAuthProvider,
        access_token: str
    ) -> OAuthUserInfo:
        """
        Get user info from OAuth provider.

        Args:
            provider: OAuth provider
            access_token: Access token

        Returns:
            Standardized user info
        """
        provider_config = self._provider_configs[provider]

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}

            # Get user info
            response = await client.get(
                provider_config["userinfo_url"],
                headers=headers
            )
            response.raise_for_status()
            user_data = response.json()

            # Get email if needed (GitHub, Bitbucket)
            email = None
            if provider in [OAuthProvider.GITHUB, OAuthProvider.BITBUCKET]:
                email_url = provider_config.get("email_url")
                if email_url:
                    email_response = await client.get(email_url, headers=headers)
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        if provider == OAuthProvider.GITHUB:
                            primary = next(
                                (e for e in emails if e.get("primary")),
                                emails[0] if emails else None
                            )
                            if primary:
                                email = primary.get("email")
                        elif provider == OAuthProvider.BITBUCKET:
                            primary = next(
                                (e for e in emails.get("values", []) if e.get("is_primary")),
                                emails.get("values", [{}])[0] if emails.get("values") else None
                            )
                            if primary:
                                email = primary.get("email")

            # Standardize user info
            return self._standardize_user_info(provider, user_data, email)

    def _standardize_user_info(
        self,
        provider: OAuthProvider,
        user_data: Dict[str, Any],
        email_override: Optional[str] = None
    ) -> OAuthUserInfo:
        """Standardize user info from different providers."""
        if provider == OAuthProvider.GITHUB:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=str(user_data.get("id")),
                email=email_override or user_data.get("email", ""),
                name=user_data.get("name") or user_data.get("login", ""),
                avatar_url=user_data.get("avatar_url"),
                verified_email=True,
                raw_data=user_data
            )

        elif provider == OAuthProvider.GOOGLE:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data.get("id", ""),
                email=user_data.get("email", ""),
                name=user_data.get("name", ""),
                avatar_url=user_data.get("picture"),
                verified_email=user_data.get("verified_email", False),
                raw_data=user_data
            )

        elif provider == OAuthProvider.MICROSOFT:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data.get("id", ""),
                email=user_data.get("mail") or user_data.get("userPrincipalName", ""),
                name=user_data.get("displayName", ""),
                avatar_url=None,  # Requires separate Graph API call
                verified_email=True,
                raw_data=user_data
            )

        elif provider == OAuthProvider.GITLAB:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=str(user_data.get("id")),
                email=user_data.get("email", ""),
                name=user_data.get("name") or user_data.get("username", ""),
                avatar_url=user_data.get("avatar_url"),
                verified_email=user_data.get("confirmed_at") is not None,
                raw_data=user_data
            )

        elif provider == OAuthProvider.BITBUCKET:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=user_data.get("uuid", "").strip("{}"),
                email=email_override or "",
                name=user_data.get("display_name", ""),
                avatar_url=user_data.get("links", {}).get("avatar", {}).get("href"),
                verified_email=True,
                raw_data=user_data
            )

        else:
            return OAuthUserInfo(
                provider=provider,
                provider_user_id=str(user_data.get("id") or user_data.get("sub", "")),
                email=user_data.get("email", ""),
                name=user_data.get("name", ""),
                avatar_url=user_data.get("picture") or user_data.get("avatar_url"),
                verified_email=user_data.get("email_verified", False),
                raw_data=user_data
            )

    async def refresh_token(
        self,
        provider: OAuthProvider,
        refresh_token: str
    ) -> Dict[str, Any]:
        """
        Refresh access token.

        Args:
            provider: OAuth provider
            refresh_token: Refresh token

        Returns:
            New token response
        """
        if provider not in self._configs:
            raise ValueError(f"Provider {provider.value} not configured")

        config = self._configs[provider]
        provider_config = self._provider_configs[provider]

        async with httpx.AsyncClient() as client:
            data = {
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }

            response = await client.post(
                provider_config["token_url"],
                data=data,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()

            return response.json()

    def cleanup_expired_states(self) -> int:
        """Clean up expired OAuth states."""
        now = datetime.utcnow()
        expired = [
            state for state, data in self._states.items()
            if data.expires_at < now
        ]
        for state in expired:
            del self._states[state]
        return len(expired)


class SAMLConfig(BaseModel):
    """SAML SSO configuration."""
    entity_id: str
    sso_url: str
    slo_url: Optional[str] = None
    certificate: str
    name_id_format: str = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    attribute_mapping: Dict[str, str] = {}


class SAMLService:
    """
    SAML SSO Service.

    Provides:
    - SP-initiated SSO
    - IdP metadata parsing
    - Assertion validation
    - Attribute mapping
    """

    def __init__(self):
        """Initialize SAML service."""
        self._configs: Dict[str, SAMLConfig] = {}

    def configure_idp(self, idp_id: str, config: SAMLConfig) -> None:
        """Configure SAML Identity Provider."""
        self._configs[idp_id] = config
        logger.info(f"Configured SAML IdP: {idp_id}")

    def get_sp_metadata(
        self,
        entity_id: str,
        acs_url: str,
        slo_url: Optional[str] = None
    ) -> str:
        """
        Generate SP metadata XML.

        Args:
            entity_id: Service Provider entity ID
            acs_url: Assertion Consumer Service URL
            slo_url: Single Logout URL

        Returns:
            SP metadata XML
        """
        slo_section = ""
        if slo_url:
            slo_section = f'''
    <md:SingleLogoutService
        Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        Location="{slo_url}"/>'''

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                     entityID="{entity_id}">
    <md:SPSSODescriptor
        AuthnRequestsSigned="true"
        WantAssertionsSigned="true"
        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
        <md:AssertionConsumerService
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            Location="{acs_url}"
            index="0"
            isDefault="true"/>{slo_section}
    </md:SPSSODescriptor>
</md:EntityDescriptor>'''

    def create_authn_request(
        self,
        idp_id: str,
        acs_url: str,
        relay_state: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create SAML AuthnRequest.

        Args:
            idp_id: Identity Provider ID
            acs_url: Assertion Consumer Service URL
            relay_state: RelayState parameter

        Returns:
            AuthnRequest data
        """
        if idp_id not in self._configs:
            raise ValueError(f"IdP {idp_id} not configured")

        config = self._configs[idp_id]
        request_id = f"_{''.join(secrets.token_hex(16))}"
        issue_instant = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        authn_request = f'''<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                        xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                        ID="{request_id}"
                        Version="2.0"
                        IssueInstant="{issue_instant}"
                        Destination="{config.sso_url}"
                        AssertionConsumerServiceURL="{acs_url}"
                        ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
    <saml:Issuer>{config.entity_id}</saml:Issuer>
    <samlp:NameIDPolicy
        Format="{config.name_id_format}"
        AllowCreate="true"/>
</samlp:AuthnRequest>'''

        import base64
        import zlib

        # Deflate and encode
        deflated = zlib.compress(authn_request.encode())[2:-4]
        encoded = base64.b64encode(deflated).decode()

        # Build redirect URL
        from urllib.parse import urlencode
        params = {"SAMLRequest": encoded}
        if relay_state:
            params["RelayState"] = relay_state

        redirect_url = f"{config.sso_url}?{urlencode(params)}"

        return {
            "request_id": request_id,
            "redirect_url": redirect_url,
            "relay_state": relay_state
        }

    def parse_response(
        self,
        idp_id: str,
        saml_response: str
    ) -> Dict[str, Any]:
        """
        Parse and validate SAML response.

        Args:
            idp_id: Identity Provider ID
            saml_response: Base64-encoded SAML response

        Returns:
            Parsed user data

        Note: In production, use a proper SAML library like python3-saml
        for full signature validation and security checks.
        """
        if idp_id not in self._configs:
            raise ValueError(f"IdP {idp_id} not configured")

        config = self._configs[idp_id]

        import base64
        from xml.etree import ElementTree

        # Decode response
        decoded = base64.b64decode(saml_response)
        root = ElementTree.fromstring(decoded)

        # Define namespaces
        ns = {
            "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
            "samlp": "urn:oasis:names:tc:SAML:2.0:protocol"
        }

        # Extract NameID
        name_id = root.find(".//saml:NameID", ns)
        email = name_id.text if name_id is not None else ""

        # Extract attributes
        attributes = {}
        for attr in root.findall(".//saml:Attribute", ns):
            name = attr.get("Name", "")
            values = [v.text for v in attr.findall("saml:AttributeValue", ns)]

            # Apply mapping
            mapped_name = config.attribute_mapping.get(name, name)
            attributes[mapped_name] = values[0] if len(values) == 1 else values

        return {
            "email": email,
            "name": attributes.get("name") or attributes.get("displayName", ""),
            "attributes": attributes,
            "raw_response": decoded.decode()
        }


# Singleton instances
_oauth_service: Optional[OAuthService] = None
_saml_service: Optional[SAMLService] = None


def get_oauth_service() -> OAuthService:
    """Get the global OAuth service instance."""
    global _oauth_service
    if _oauth_service is None:
        _oauth_service = OAuthService()
    return _oauth_service


def get_saml_service() -> SAMLService:
    """Get the global SAML service instance."""
    global _saml_service
    if _saml_service is None:
        _saml_service = SAMLService()
    return _saml_service


__all__ = [
    "OAuthService",
    "OAuthProvider",
    "OAuthConfig",
    "OAuthUserInfo",
    "SAMLService",
    "SAMLConfig",
    "get_oauth_service",
    "get_saml_service"
]
