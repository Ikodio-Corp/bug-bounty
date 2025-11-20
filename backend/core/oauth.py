"""
OAuth2 and SSO Authentication Service
Supports Google, GitHub, Microsoft, GitLab
"""

import asyncio
import aiohttp
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
from urllib.parse import urlencode


class OAuth2Provider:
    """Base OAuth2 provider"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def generate_state(self) -> str:
        """Generate state parameter for CSRF protection"""
        return secrets.token_urlsafe(32)
    
    def get_authorization_url(self, state: str, scope: str) -> str:
        """Get OAuth2 authorization URL"""
        raise NotImplementedError
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        raise NotImplementedError


class GoogleOAuth2(OAuth2Provider):
    """Google OAuth2 provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self, state: str, scope: str = "email profile") -> str:
        """Get Google OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Token exchange failed: {response.status}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.userinfo_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "provider": "google",
                        "provider_user_id": data.get("id"),
                        "email": data.get("email"),
                        "email_verified": data.get("verified_email"),
                        "name": data.get("name"),
                        "picture": data.get("picture"),
                        "locale": data.get("locale")
                    }
                else:
                    raise Exception(f"Failed to get user info: {response.status}")


class GitHubOAuth2(OAuth2Provider):
    """GitHub OAuth2 provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        super().__init__(client_id, client_secret, redirect_uri)
        self.auth_url = "https://github.com/login/oauth/authorize"
        self.token_url = "https://github.com/login/oauth/access_token"
        self.userinfo_url = "https://api.github.com/user"
        self.emails_url = "https://api.github.com/user/emails"
    
    def get_authorization_url(self, state: str, scope: str = "read:user user:email") -> str:
        """Get GitHub OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {"Accept": "application/json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.token_url,
                data=data,
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Token exchange failed: {response.status}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from GitHub"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.userinfo_url, headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    
                    async with session.get(self.emails_url, headers=headers) as email_response:
                        emails = await email_response.json() if email_response.status == 200 else []
                        primary_email = next(
                            (e for e in emails if e.get("primary")),
                            {"email": user_data.get("email"), "verified": False}
                        )
                    
                    return {
                        "provider": "github",
                        "provider_user_id": str(user_data.get("id")),
                        "email": primary_email.get("email"),
                        "email_verified": primary_email.get("verified"),
                        "name": user_data.get("name") or user_data.get("login"),
                        "username": user_data.get("login"),
                        "picture": user_data.get("avatar_url"),
                        "bio": user_data.get("bio"),
                        "location": user_data.get("location"),
                        "website": user_data.get("blog")
                    }
                else:
                    raise Exception(f"Failed to get user info: {response.status}")


class MicrosoftOAuth2(OAuth2Provider):
    """Microsoft OAuth2 provider"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant: str = "common"):
        super().__init__(client_id, client_secret, redirect_uri)
        self.tenant = tenant
        self.auth_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        self.userinfo_url = "https://graph.microsoft.com/v1.0/me"
    
    def get_authorization_url(self, state: str, scope: str = "openid profile email") -> str:
        """Get Microsoft OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "response_mode": "query"
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "scope": "openid profile email"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Token exchange failed: {response.status}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Microsoft"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.userinfo_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "provider": "microsoft",
                        "provider_user_id": data.get("id"),
                        "email": data.get("mail") or data.get("userPrincipalName"),
                        "email_verified": True,
                        "name": data.get("displayName"),
                        "given_name": data.get("givenName"),
                        "family_name": data.get("surname"),
                        "job_title": data.get("jobTitle")
                    }
                else:
                    raise Exception(f"Failed to get user info: {response.status}")


class GitLabOAuth2(OAuth2Provider):
    """GitLab OAuth2 provider"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        gitlab_url: str = "https://gitlab.com"
    ):
        super().__init__(client_id, client_secret, redirect_uri)
        self.gitlab_url = gitlab_url
        self.auth_url = f"{gitlab_url}/oauth/authorize"
        self.token_url = f"{gitlab_url}/oauth/token"
        self.userinfo_url = f"{gitlab_url}/api/v4/user"
    
    def get_authorization_url(self, state: str, scope: str = "read_user") -> str:
        """Get GitLab OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Token exchange failed: {response.status}")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from GitLab"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.userinfo_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "provider": "gitlab",
                        "provider_user_id": str(data.get("id")),
                        "email": data.get("email"),
                        "email_verified": data.get("confirmed_at") is not None,
                        "name": data.get("name"),
                        "username": data.get("username"),
                        "picture": data.get("avatar_url"),
                        "bio": data.get("bio"),
                        "location": data.get("location"),
                        "website": data.get("website_url")
                    }
                else:
                    raise Exception(f"Failed to get user info: {response.status}")


class SSOManager:
    """Manage all SSO providers"""
    
    def __init__(self, config: Dict[str, Dict[str, str]]):
        self.providers = {}
        
        if "google" in config:
            self.providers["google"] = GoogleOAuth2(**config["google"])
        
        if "github" in config:
            self.providers["github"] = GitHubOAuth2(**config["github"])
        
        if "microsoft" in config:
            self.providers["microsoft"] = MicrosoftOAuth2(**config["microsoft"])
        
        if "gitlab" in config:
            self.providers["gitlab"] = GitLabOAuth2(**config["gitlab"])
    
    def get_provider(self, provider_name: str) -> Optional[OAuth2Provider]:
        """Get OAuth2 provider by name"""
        return self.providers.get(provider_name)
    
    def get_authorization_url(self, provider_name: str, state: str) -> str:
        """Get authorization URL for provider"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not configured")
        
        return provider.get_authorization_url(state)
    
    async def authenticate(
        self,
        provider_name: str,
        code: str
    ) -> Dict[str, Any]:
        """Complete OAuth2 authentication flow"""
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider {provider_name} not configured")
        
        token_data = await provider.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise Exception("No access token received")
        
        user_info = await provider.get_user_info(access_token)
        
        return {
            "user_info": user_info,
            "access_token": access_token,
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data.get("expires_in")
        }
