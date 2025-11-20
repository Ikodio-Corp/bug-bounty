"""
API Documentation Generator
OpenAPI/Swagger specification and documentation
"""
from fastapi import APIRouter, HTTPException
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any, List
import json

router = APIRouter(prefix="/api-docs", tags=["API Documentation"])


def generate_openapi_spec(app) -> Dict[str, Any]:
    """Generate OpenAPI specification"""
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="IKODIO BugBounty Platform API",
        version="1.0.0",
        description="""
# IKODIO BugBounty Platform API

## Overview
IKODIO is an AI-powered bug bounty automation platform that discovers, validates, and reports security vulnerabilities in 90 seconds.

## Features
- AI-powered vulnerability detection using GPT-4 and CodeBERT
- Multi-scanner integration (SCA, Secret, Container, IaC)
- OAuth2/SSO authentication with 2FA support
- VCS integration (GitHub, GitLab)
- CI/CD integration (Jenkins, GitHub Actions, GitLab CI, CircleCI)
- Cloud provider security integration (AWS, GCP, Azure)
- Bug validation workflow with peer review
- Duplicate detection using ML-based similarity
- Issue tracking integration (Jira, Linear, Asana, Monday)
- Auto-reporting to bug bounty platforms (HackerOne, Bugcrowd, Intigriti)
- Advanced RBAC with granular permissions
- Payment and subscription management

## Authentication
Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

To obtain a token:
1. Register: POST /api/auth/register
2. Login: POST /api/auth/login
3. Use the returned access_token in subsequent requests

## Rate Limiting
- Free tier: 100 requests/hour
- Bronze tier: 1000 requests/hour
- Silver tier: 5000 requests/hour
- Gold tier: Unlimited

## Support
- Documentation: https://docs.ikodio.com
- Support: support@ikodio.com
- Status: https://status.ikodio.com
        """,
        routes=app.routes,
        servers=[
            {
                "url": "https://api.ikodio.com",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.ikodio.com",
                "description": "Staging server"
            },
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ],
        tags=[
            {
                "name": "Authentication",
                "description": "User authentication and authorization"
            },
            {
                "name": "OAuth2/SSO",
                "description": "OAuth2 and Single Sign-On integration"
            },
            {
                "name": "Two-Factor Authentication",
                "description": "2FA and WebAuthn/FIDO2 support"
            },
            {
                "name": "Users",
                "description": "User management and profiles"
            },
            {
                "name": "Bugs",
                "description": "Bug and vulnerability management"
            },
            {
                "name": "Bug Validation",
                "description": "Multi-stage bug validation workflow"
            },
            {
                "name": "Duplicate Detection",
                "description": "ML-based duplicate bug detection"
            },
            {
                "name": "Scans",
                "description": "Security scanning operations"
            },
            {
                "name": "Advanced Scanners",
                "description": "SCA, Secret, Container, and IaC scanning"
            },
            {
                "name": "ML Pipeline",
                "description": "AI-powered 90-second vulnerability detection"
            },
            {
                "name": "VCS Integration",
                "description": "GitHub and GitLab integration"
            },
            {
                "name": "CI/CD Integration",
                "description": "Jenkins, GitHub Actions, GitLab CI, CircleCI"
            },
            {
                "name": "Cloud Security",
                "description": "AWS, GCP, Azure security integration"
            },
            {
                "name": "Issue Tracking",
                "description": "Jira, Linear, Asana, Monday integration"
            },
            {
                "name": "Auto Reporting",
                "description": "Automatic reporting to bug bounty platforms"
            },
            {
                "name": "Notifications",
                "description": "Email, Slack, Discord notifications"
            },
            {
                "name": "Payments & Subscriptions",
                "description": "Stripe payment and subscription management"
            },
            {
                "name": "RBAC",
                "description": "Role-Based Access Control"
            },
            {
                "name": "Marketplace",
                "description": "Bug marketplace and trading"
            },
            {
                "name": "Guild",
                "description": "Hunter guilds and teams"
            },
            {
                "name": "Health",
                "description": "Health checks and system status"
            }
        ]
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authentication token"
        },
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "/api/oauth/google/login",
                    "tokenUrl": "/api/auth/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access",
                        "admin": "Admin access"
                    }
                }
            }
        }
    }
    
    # Add response schemas
    openapi_schema["components"]["schemas"]["Error"] = {
        "type": "object",
        "properties": {
            "detail": {
                "type": "string",
                "description": "Error message"
            }
        }
    }
    
    openapi_schema["components"]["schemas"]["Success"] = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Operation status"
            },
            "message": {
                "type": "string",
                "description": "Success message"
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@router.get("/openapi.json")
async def get_openapi_json():
    """
    Get OpenAPI specification in JSON format
    
    Returns:
        dict: OpenAPI specification
    """
    from main import app
    return generate_openapi_spec(app)


@router.get("/openapi.yaml")
async def get_openapi_yaml():
    """
    Get OpenAPI specification in YAML format
    
    Returns:
        str: OpenAPI specification as YAML
    """
    import yaml
    from main import app
    
    openapi_dict = generate_openapi_spec(app)
    return yaml.dump(openapi_dict, default_flow_style=False)


@router.get("/postman")
async def get_postman_collection():
    """
    Generate Postman collection
    
    Returns:
        dict: Postman collection
    """
    from main import app
    openapi_spec = generate_openapi_spec(app)
    
    postman_collection = {
        "info": {
            "name": "IKODIO BugBounty API",
            "description": openapi_spec["info"]["description"],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [],
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{access_token}}",
                    "type": "string"
                }
            ]
        },
        "variable": [
            {
                "key": "base_url",
                "value": "https://api.ikodio.com",
                "type": "string"
            },
            {
                "key": "access_token",
                "value": "",
                "type": "string"
            }
        ]
    }
    
    # Convert OpenAPI paths to Postman requests
    for path, methods in openapi_spec["paths"].items():
        for method, details in methods.items():
            request_item = {
                "name": details.get("summary", path),
                "request": {
                    "method": method.upper(),
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json"
                        }
                    ],
                    "url": {
                        "raw": "{{base_url}}" + path,
                        "host": ["{{base_url}}"],
                        "path": path.split("/")[1:]
                    },
                    "description": details.get("description", "")
                }
            }
            
            # Add request body if present
            if "requestBody" in details:
                request_item["request"]["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(
                        details["requestBody"].get("content", {})
                        .get("application/json", {})
                        .get("example", {}),
                        indent=2
                    )
                }
            
            postman_collection["item"].append(request_item)
    
    return postman_collection


@router.get("/endpoints")
async def list_endpoints():
    """
    List all API endpoints
    
    Returns:
        dict: List of endpoints grouped by tag
    """
    from main import app
    openapi_spec = generate_openapi_spec(app)
    
    endpoints = {}
    
    for path, methods in openapi_spec["paths"].items():
        for method, details in methods.items():
            tags = details.get("tags", ["Other"])
            for tag in tags:
                if tag not in endpoints:
                    endpoints[tag] = []
                
                endpoints[tag].append({
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "requires_auth": "security" in details
                })
    
    return {
        "endpoints": endpoints,
        "total": sum(len(v) for v in endpoints.values())
    }


@router.get("/changelog")
async def get_api_changelog():
    """
    Get API changelog
    
    Returns:
        dict: API changelog
    """
    changelog = {
        "versions": [
            {
                "version": "1.0.0",
                "date": "2024-01-15",
                "changes": [
                    "Initial API release",
                    "OAuth2/SSO integration (Google, GitHub, Microsoft, GitLab)",
                    "Two-Factor Authentication (TOTP, WebAuthn)",
                    "Advanced scanners (SCA, Secret, Container, IaC)",
                    "Payment and subscription management",
                    "VCS integration (GitHub, GitLab)",
                    "CI/CD integration (4 platforms)",
                    "Notification system (Email, Slack, Discord)",
                    "ML Pipeline for 90-second scanning",
                    "Bug validation workflow",
                    "Duplicate detection",
                    "Issue tracking integration (4 platforms)",
                    "Auto-reporting to bug bounty platforms (4 platforms)",
                    "Cloud provider security integration (AWS, GCP, Azure)",
                    "Advanced RBAC system"
                ],
                "breaking_changes": []
            }
        ]
    }
    
    return changelog


@router.get("/stats")
async def get_api_stats():
    """
    Get API statistics
    
    Returns:
        dict: API statistics
    """
    from main import app
    openapi_spec = generate_openapi_spec(app)
    
    total_endpoints = sum(len(methods) for methods in openapi_spec["paths"].values())
    
    methods_count = {}
    for methods in openapi_spec["paths"].values():
        for method in methods.keys():
            methods_count[method.upper()] = methods_count.get(method.upper(), 0) + 1
    
    tags_count = {}
    for methods in openapi_spec["paths"].values():
        for details in methods.values():
            for tag in details.get("tags", []):
                tags_count[tag] = tags_count.get(tag, 0) + 1
    
    return {
        "total_endpoints": total_endpoints,
        "methods": methods_count,
        "tags": tags_count,
        "version": openapi_spec["info"]["version"],
        "openapi_version": openapi_spec["openapi"]
    }


@router.get("/examples/{tag}")
async def get_code_examples(tag: str):
    """
    Get code examples for specific tag
    
    Args:
        tag: API tag/category
        
    Returns:
        dict: Code examples in multiple languages
    """
    examples = {
        "Authentication": {
            "python": """
import requests

# Register
response = requests.post(
    "https://api.ikodio.com/api/auth/register",
    json={
        "email": "user@example.com",
        "username": "hunter1",
        "password": "SecurePass123!",
        "full_name": "John Doe"
    }
)

# Login
response = requests.post(
    "https://api.ikodio.com/api/auth/login",
    data={
        "username": "user@example.com",
        "password": "SecurePass123!"
    }
)
token = response.json()["access_token"]

# Use token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "https://api.ikodio.com/api/users/me",
    headers=headers
)
            """,
            "javascript": """
// Register
const response = await fetch('https://api.ikodio.com/api/auth/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        email: 'user@example.com',
        username: 'hunter1',
        password: 'SecurePass123!',
        full_name: 'John Doe'
    })
});

// Login
const loginResponse = await fetch('https://api.ikodio.com/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
        username: 'user@example.com',
        password: 'SecurePass123!'
    })
});
const { access_token } = await loginResponse.json();

// Use token
const userResponse = await fetch('https://api.ikodio.com/api/users/me', {
    headers: {
        'Authorization': `Bearer ${access_token}`
    }
});
            """,
            "curl": """
# Register
curl -X POST https://api.ikodio.com/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "username": "hunter1",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'

# Login
curl -X POST https://api.ikodio.com/api/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=user@example.com&password=SecurePass123!"

# Use token
curl https://api.ikodio.com/api/users/me \\
  -H "Authorization: Bearer <token>"
            """
        },
        "Scans": {
            "python": """
import requests

headers = {"Authorization": f"Bearer {token}"}

# Start scan
response = requests.post(
    "https://api.ikodio.com/api/ml-pipeline/quick-scan",
    headers=headers,
    json={
        "target_url": "https://example.com",
        "scan_type": "full"
    }
)
scan_id = response.json()["scan_id"]

# Get scan results
response = requests.get(
    f"https://api.ikodio.com/api/scans/{scan_id}",
    headers=headers
)
results = response.json()
            """
        }
    }
    
    if tag not in examples:
        raise HTTPException(status_code=404, detail=f"No examples found for tag: {tag}")
    
    return {
        "tag": tag,
        "examples": examples[tag]
    }
