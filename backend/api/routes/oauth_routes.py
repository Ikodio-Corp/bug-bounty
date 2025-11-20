"""
OAuth/SSO API Routes - Authentication Endpoints

This module provides REST API endpoints for OAuth2 and SAML SSO authentication.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...auth.oauth_providers import (
    get_oauth_service,
    get_saml_service,
    OAuthService,
    SAMLService,
    OAuthProvider,
    OAuthConfig
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/oauth", tags=["OAuth/SSO"])


# Request Models
class OAuthCallbackRequest(BaseModel):
    """OAuth callback request."""
    code: str = Field(..., description="Authorization code")
    state: str = Field(..., description="State parameter")


class ConfigureProviderRequest(BaseModel):
    """Request to configure OAuth provider."""
    provider: str = Field(..., description="Provider name")
    client_id: str = Field(..., description="Client ID")
    client_secret: str = Field(..., description="Client secret")
    redirect_uri: str = Field(..., description="Redirect URI")
    scopes: list = Field(default=[], description="OAuth scopes")


# Dependencies
async def get_oauth() -> OAuthService:
    """Get OAuth service."""
    return get_oauth_service()


async def get_saml() -> SAMLService:
    """Get SAML service."""
    return get_saml_service()


# OAuth Endpoints
@router.get("/authorize/{provider}", response_model=Dict[str, Any])
async def get_authorization_url(
    provider: str,
    redirect_url: Optional[str] = Query(None, description="URL to redirect after auth"),
    service: OAuthService = Depends(get_oauth)
):
    """
    Get OAuth authorization URL.

    Initiates OAuth flow by returning the authorization URL
    for the specified provider.
    """
    try:
        oauth_provider = OAuthProvider(provider)
        result = service.get_authorization_url(oauth_provider, redirect_url)

        return {
            "success": True,
            "provider": provider,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Get authorization URL failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/callback/{provider}", response_model=Dict[str, Any])
async def oauth_callback(
    provider: str,
    request: OAuthCallbackRequest,
    service: OAuthService = Depends(get_oauth)
):
    """
    Handle OAuth callback.

    Exchanges authorization code for tokens and retrieves user info.
    """
    try:
        oauth_provider = OAuthProvider(provider)

        # Exchange code for tokens
        token_data = await service.exchange_code(
            oauth_provider,
            request.code,
            request.state
        )

        # Get user info
        user_info = await service.get_user_info(
            oauth_provider,
            token_data["access_token"]
        )

        return {
            "success": True,
            "provider": provider,
            "user": {
                "provider_user_id": user_info.provider_user_id,
                "email": user_info.email,
                "name": user_info.name,
                "avatar_url": user_info.avatar_url,
                "verified_email": user_info.verified_email
            },
            "tokens": {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "token_type": token_data["token_type"],
                "expires_in": token_data.get("expires_in")
            },
            "redirect_url": token_data.get("redirect_url")
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/callback/{provider}", response_model=Dict[str, Any])
async def oauth_callback_get(
    provider: str,
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="State parameter"),
    service: OAuthService = Depends(get_oauth)
):
    """
    Handle OAuth callback (GET).

    Alternative callback handler for providers that use GET redirects.
    """
    request = OAuthCallbackRequest(code=code, state=state)
    return await oauth_callback(provider, request, service)


@router.post("/refresh/{provider}", response_model=Dict[str, Any])
async def refresh_token(
    provider: str,
    refresh_token: str = Query(..., description="Refresh token"),
    service: OAuthService = Depends(get_oauth)
):
    """
    Refresh OAuth access token.

    Uses refresh token to get new access token.
    """
    try:
        oauth_provider = OAuthProvider(provider)
        result = await service.refresh_token(oauth_provider, refresh_token)

        return {
            "success": True,
            "provider": provider,
            "access_token": result.get("access_token"),
            "refresh_token": result.get("refresh_token"),
            "expires_in": result.get("expires_in")
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/configure", response_model=Dict[str, Any])
async def configure_provider(
    request: ConfigureProviderRequest,
    service: OAuthService = Depends(get_oauth)
):
    """
    Configure OAuth provider.

    Sets up OAuth provider with client credentials.
    Admin only endpoint.
    """
    try:
        config = OAuthConfig(
            provider=OAuthProvider(request.provider),
            client_id=request.client_id,
            client_secret=request.client_secret,
            redirect_uri=request.redirect_uri,
            scopes=request.scopes
        )

        service.configure_provider(config)

        return {
            "success": True,
            "message": f"Provider {request.provider} configured successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Configure provider failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=Dict[str, Any])
async def get_supported_providers():
    """Get list of supported OAuth providers."""
    return {
        "success": True,
        "providers": [
            {"id": "github", "name": "GitHub", "icon": "github"},
            {"id": "google", "name": "Google", "icon": "google"},
            {"id": "microsoft", "name": "Microsoft", "icon": "microsoft"},
            {"id": "gitlab", "name": "GitLab", "icon": "gitlab"},
            {"id": "bitbucket", "name": "Bitbucket", "icon": "bitbucket"}
        ]
    }


# SAML Endpoints
@router.get("/saml/metadata", response_model=Dict[str, Any])
async def get_sp_metadata(
    entity_id: str = Query(..., description="SP Entity ID"),
    acs_url: str = Query(..., description="Assertion Consumer Service URL"),
    slo_url: Optional[str] = Query(None, description="Single Logout URL"),
    service: SAMLService = Depends(get_saml)
):
    """
    Get SAML SP metadata.

    Returns Service Provider metadata XML for IdP configuration.
    """
    try:
        metadata = service.get_sp_metadata(entity_id, acs_url, slo_url)

        return {
            "success": True,
            "content_type": "application/xml",
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"Get SP metadata failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/saml/login/{idp_id}", response_model=Dict[str, Any])
async def saml_login(
    idp_id: str,
    acs_url: str = Query(..., description="Assertion Consumer Service URL"),
    relay_state: Optional[str] = Query(None, description="RelayState"),
    service: SAMLService = Depends(get_saml)
):
    """
    Initiate SAML SSO login.

    Creates AuthnRequest and returns redirect URL to IdP.
    """
    try:
        result = service.create_authn_request(idp_id, acs_url, relay_state)

        return {
            "success": True,
            "idp_id": idp_id,
            **result
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"SAML login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/saml/acs/{idp_id}", response_model=Dict[str, Any])
async def saml_acs(
    idp_id: str,
    saml_response: str = Query(..., alias="SAMLResponse"),
    relay_state: Optional[str] = Query(None, alias="RelayState"),
    service: SAMLService = Depends(get_saml)
):
    """
    Handle SAML Assertion Consumer Service.

    Processes SAML response and extracts user information.
    """
    try:
        result = service.parse_response(idp_id, saml_response)

        return {
            "success": True,
            "idp_id": idp_id,
            "user": {
                "email": result["email"],
                "name": result["name"],
                "attributes": result["attributes"]
            },
            "relay_state": relay_state
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"SAML ACS failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
