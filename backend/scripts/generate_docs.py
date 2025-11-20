"""
API Documentation Generator
Automatically generates OpenAPI documentation for IKODIO BugBounty platform
"""

import json
from pathlib import Path
from typing import Dict, Any
from backend.main import app


def generate_openapi_spec() -> Dict[str, Any]:
    """Generate OpenAPI specification from FastAPI app"""
    return app.openapi()


def save_openapi_json(output_path: str = "docs/api/openapi.json"):
    """Save OpenAPI spec to JSON file"""
    spec = generate_openapi_spec()
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(spec, f, indent=2)
    
    print(f"OpenAPI specification saved to: {output_file}")
    return spec


def generate_markdown_docs(spec: Dict[str, Any], output_path: str = "docs/api/API.md"):
    """Generate Markdown documentation from OpenAPI spec"""
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        # Header
        f.write(f"# {spec['info']['title']}\n\n")
        f.write(f"{spec['info']['description']}\n\n")
        f.write(f"**Version:** {spec['info']['version']}\n\n")
        
        # Base URL
        if 'servers' in spec:
            f.write("## Base URLs\n\n")
            for server in spec['servers']:
                f.write(f"- {server['url']}\n")
            f.write("\n")
        
        # Authentication
        if 'components' in spec and 'securitySchemes' in spec['components']:
            f.write("## Authentication\n\n")
            for name, scheme in spec['components']['securitySchemes'].items():
                f.write(f"### {name}\n\n")
                f.write(f"- **Type:** {scheme['type']}\n")
                if 'scheme' in scheme:
                    f.write(f"- **Scheme:** {scheme['scheme']}\n")
                if 'bearerFormat' in scheme:
                    f.write(f"- **Format:** {scheme['bearerFormat']}\n")
                f.write("\n")
        
        # Endpoints by tag
        if 'paths' in spec:
            # Group by tags
            endpoints_by_tag: Dict[str, list] = {}
            
            for path, methods in spec['paths'].items():
                for method, details in methods.items():
                    if method in ['get', 'post', 'put', 'patch', 'delete']:
                        tags = details.get('tags', ['Other'])
                        for tag in tags:
                            if tag not in endpoints_by_tag:
                                endpoints_by_tag[tag] = []
                            endpoints_by_tag[tag].append({
                                'path': path,
                                'method': method.upper(),
                                'details': details
                            })
            
            # Write endpoints
            for tag, endpoints in sorted(endpoints_by_tag.items()):
                f.write(f"## {tag}\n\n")
                
                for endpoint in endpoints:
                    f.write(f"### {endpoint['method']} {endpoint['path']}\n\n")
                    
                    details = endpoint['details']
                    
                    # Summary and description
                    if 'summary' in details:
                        f.write(f"**{details['summary']}**\n\n")
                    if 'description' in details:
                        f.write(f"{details['description']}\n\n")
                    
                    # Parameters
                    if 'parameters' in details:
                        f.write("**Parameters:**\n\n")
                        for param in details['parameters']:
                            required = " (required)" if param.get('required') else ""
                            f.write(f"- `{param['name']}` ({param['in']}){required}: {param.get('description', '')}\n")
                        f.write("\n")
                    
                    # Request body
                    if 'requestBody' in details:
                        f.write("**Request Body:**\n\n")
                        content = details['requestBody'].get('content', {})
                        for content_type, schema_info in content.items():
                            f.write(f"Content-Type: `{content_type}`\n\n")
                            if 'schema' in schema_info:
                                f.write("```json\n")
                                f.write(json.dumps(schema_info['schema'], indent=2))
                                f.write("\n```\n\n")
                    
                    # Responses
                    if 'responses' in details:
                        f.write("**Responses:**\n\n")
                        for status_code, response in details['responses'].items():
                            f.write(f"- **{status_code}**: {response.get('description', '')}\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
    
    print(f"Markdown documentation saved to: {output_file}")


def generate_postman_collection(spec: Dict[str, Any], output_path: str = "docs/api/postman_collection.json"):
    """Generate Postman collection from OpenAPI spec"""
    
    collection = {
        "info": {
            "name": spec['info']['title'],
            "description": spec['info']['description'],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }
    
    # Group by tags
    folders: Dict[str, list] = {}
    
    for path, methods in spec.get('paths', {}).items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'patch', 'delete']:
                tags = details.get('tags', ['Other'])
                
                # Create request
                request = {
                    "name": details.get('summary', f"{method.upper()} {path}"),
                    "request": {
                        "method": method.upper(),
                        "header": [],
                        "url": {
                            "raw": f"{{{{base_url}}}}{path}",
                            "host": ["{{base_url}}"],
                            "path": path.strip('/').split('/')
                        }
                    }
                }
                
                # Add to folder
                for tag in tags:
                    if tag not in folders:
                        folders[tag] = []
                    folders[tag].append(request)
    
    # Add folders to collection
    for folder_name, requests in sorted(folders.items()):
        collection['item'].append({
            "name": folder_name,
            "item": requests
        })
    
    # Add variables
    collection['variable'] = [
        {
            "key": "base_url",
            "value": "http://localhost:8000",
            "type": "string"
        }
    ]
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(collection, f, indent=2)
    
    print(f"Postman collection saved to: {output_file}")


if __name__ == "__main__":
    print("Generating API documentation...")
    
    # Generate OpenAPI JSON
    spec = save_openapi_json()
    
    # Generate Markdown docs
    generate_markdown_docs(spec)
    
    # Generate Postman collection
    generate_postman_collection(spec)
    
    print("\nDocumentation generation complete!")
    print("\nGenerated files:")
    print("- docs/api/openapi.json")
    print("- docs/api/API.md")
    print("- docs/api/postman_collection.json")
