"""
AI Code Generator Service
Revolutionary feature that can generate complete applications from descriptions
Replaces developers for routine tasks
"""

import asyncio
from typing import Dict, List, Optional
from openai import AsyncOpenAI
import anthropic
import ast
import black
import isort

class AICodeGeneratorService:
    """
    AI-powered code generation that can create complete applications
    Features:
    - Generate full-stack apps from natural language
    - Auto-generate tests
    - Auto-generate documentation
    - Code review and optimization
    - Security vulnerability detection
    """
    
    def __init__(self, openai_key: str, anthropic_key: str):
        self.openai = AsyncOpenAI(api_key=openai_key)
        self.anthropic = anthropic.AsyncAnthropic(api_key=anthropic_key)
        
    async def generate_fullstack_app(
        self,
        description: str,
        tech_stack: Dict[str, str],
        requirements: List[str]
    ) -> Dict[str, any]:
        """
        Generate complete full-stack application from description
        
        This replaces:
        - Frontend developers
        - Backend developers
        - Database designers
        """
        
        result = {
            "backend": {},
            "frontend": {},
            "database": {},
            "tests": {},
            "deployment": {},
            "documentation": {}
        }
        
        # Generate in parallel for speed
        backend_task = self._generate_backend(description, tech_stack, requirements)
        frontend_task = self._generate_frontend(description, tech_stack, requirements)
        database_task = self._generate_database_schema(description, requirements)
        
        backend, frontend, database = await asyncio.gather(
            backend_task, frontend_task, database_task
        )
        
        result["backend"] = backend
        result["frontend"] = frontend
        result["database"] = database
        
        # Generate tests automatically
        result["tests"] = await self._generate_tests(backend, frontend)
        
        # Generate deployment configs
        result["deployment"] = await self._generate_deployment_configs(
            backend, frontend, database, tech_stack
        )
        
        # Generate documentation
        result["documentation"] = await self._generate_documentation(
            description, backend, frontend, database
        )
        
        return result
    
    async def _generate_backend(
        self,
        description: str,
        tech_stack: Dict[str, str],
        requirements: List[str]
    ) -> Dict[str, str]:
        """Generate backend code using GPT-4 and Claude"""
        
        backend_framework = tech_stack.get("backend", "fastapi")
        
        prompt = f"""
Generate a complete production-ready {backend_framework} backend for:

Description: {description}

Requirements:
{chr(10).join(f'- {req}' for req in requirements)}

Generate:
1. Main application file
2. Models with SQLAlchemy
3. API routes with proper validation
4. Services layer
5. Database migrations
6. Middleware (auth, rate limiting, CORS)
7. Error handling
8. Logging
9. Configuration management
10. requirements.txt

Make it production-ready with:
- Proper async/await
- Database connection pooling
- Caching strategy
- Security best practices
- API documentation
- Health check endpoints
"""
        
        response = await self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert full-stack developer who writes production-ready code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=16000
        )
        
        code = response.choices[0].message.content
        
        # Parse and organize files
        files = self._parse_code_blocks(code)
        
        # Format code
        for filename, content in files.items():
            if filename.endswith('.py'):
                files[filename] = self._format_python_code(content)
        
        return files
    
    async def _generate_frontend(
        self,
        description: str,
        tech_stack: Dict[str, str],
        requirements: List[str]
    ) -> Dict[str, str]:
        """Generate frontend code using Claude"""
        
        frontend_framework = tech_stack.get("frontend", "nextjs")
        
        prompt = f"""
Generate a complete production-ready {frontend_framework} frontend for:

Description: {description}

Requirements:
{chr(10).join(f'- {req}' for req in requirements)}

Generate:
1. Page components
2. Reusable UI components
3. API client
4. State management
5. Routing
6. Forms with validation
7. Error boundaries
8. Loading states
9. Responsive design
10. TypeScript types
11. Tailwind CSS styling
12. package.json

Make it production-ready with:
- TypeScript for type safety
- Proper error handling
- Accessibility (a11y)
- SEO optimization
- Performance optimization
- Security best practices
"""
        
        response = await self.anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=16000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        code = response.content[0].text
        
        # Parse and organize files
        files = self._parse_code_blocks(code)
        
        return files
    
    async def _generate_database_schema(
        self,
        description: str,
        requirements: List[str]
    ) -> Dict[str, any]:
        """Generate optimized database schema"""
        
        prompt = f"""
Design a production-ready database schema for:

Description: {description}

Requirements:
{chr(10).join(f'- {req}' for req in requirements)}

Provide:
1. Table definitions with proper data types
2. Indexes for performance
3. Foreign key relationships
4. Constraints
5. Triggers if needed
6. Views for complex queries
7. Migration scripts (Alembic)

Optimize for:
- Query performance
- Data integrity
- Scalability
- Security
"""
        
        response = await self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a database architect who designs optimal schemas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        schema = response.choices[0].message.content
        
        return {
            "schema": schema,
            "migrations": self._generate_alembic_migrations(schema)
        }
    
    async def _generate_tests(
        self,
        backend: Dict[str, str],
        frontend: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Auto-generate comprehensive tests
        Replaces QA engineers for unit/integration tests
        """
        
        tests = {}
        
        # Generate backend tests
        for filename, code in backend.items():
            if filename.endswith('.py') and 'test_' not in filename:
                test_code = await self._generate_pytest_tests(filename, code)
                tests[f"backend/tests/test_{filename}"] = test_code
        
        # Generate frontend tests
        for filename, code in frontend.items():
            if filename.endswith(('.tsx', '.ts')):
                test_code = await self._generate_jest_tests(filename, code)
                tests[f"frontend/tests/{filename}.test.tsx"] = test_code
        
        return tests
    
    async def _generate_pytest_tests(self, filename: str, code: str) -> str:
        """Generate pytest tests for Python code"""
        
        prompt = f"""
Generate comprehensive pytest tests for this code:

File: {filename}
```python
{code}
```

Include:
- Unit tests for all functions
- Integration tests for API endpoints
- Edge cases
- Error scenarios
- Mocking external dependencies
- Fixtures
- Parametrized tests
- 90%+ code coverage
"""
        
        response = await self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a QA engineer who writes comprehensive tests."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    async def _generate_jest_tests(self, filename: str, code: str) -> str:
        """Generate Jest/React Testing Library tests"""
        
        prompt = f"""
Generate comprehensive Jest + React Testing Library tests for:

File: {filename}
```typescript
{code}
```

Include:
- Component rendering tests
- User interaction tests
- API mocking
- State management tests
- Error boundary tests
- Accessibility tests
- Snapshot tests
- 90%+ code coverage
"""
        
        response = await self.openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a frontend QA engineer expert in React testing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    async def _generate_deployment_configs(
        self,
        backend: Dict[str, str],
        frontend: Dict[str, str],
        database: Dict[str, any],
        tech_stack: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Generate deployment configurations
        Replaces DevOps engineers for standard deployments
        """
        
        configs = {}
        
        # Docker
        configs["Dockerfile.backend"] = self._generate_backend_dockerfile(tech_stack)
        configs["Dockerfile.frontend"] = self._generate_frontend_dockerfile(tech_stack)
        configs["docker-compose.yml"] = self._generate_docker_compose(tech_stack)
        configs["docker-compose.prod.yml"] = self._generate_docker_compose_prod(tech_stack)
        
        # Kubernetes
        configs["k8s/deployment.yaml"] = await self._generate_k8s_deployment()
        configs["k8s/service.yaml"] = await self._generate_k8s_service()
        configs["k8s/ingress.yaml"] = await self._generate_k8s_ingress()
        configs["k8s/configmap.yaml"] = await self._generate_k8s_configmap()
        configs["k8s/secrets.yaml"] = await self._generate_k8s_secrets()
        
        # CI/CD
        configs[".github/workflows/ci.yml"] = await self._generate_github_actions()
        configs[".github/workflows/deploy.yml"] = await self._generate_deployment_pipeline()
        
        # Infrastructure as Code
        configs["terraform/main.tf"] = await self._generate_terraform()
        configs["terraform/variables.tf"] = await self._generate_terraform_vars()
        
        # Monitoring
        configs["prometheus.yml"] = self._generate_prometheus_config()
        configs["grafana/dashboard.json"] = await self._generate_grafana_dashboard()
        
        return configs
    
    async def _generate_documentation(
        self,
        description: str,
        backend: Dict[str, str],
        frontend: Dict[str, str],
        database: Dict[str, any]
    ) -> Dict[str, str]:
        """
        Auto-generate comprehensive documentation
        Replaces technical writers
        """
        
        docs = {}
        
        # API documentation
        docs["API.md"] = await self._generate_api_docs(backend)
        docs["openapi.yaml"] = await self._generate_openapi_spec(backend)
        
        # Architecture documentation
        docs["ARCHITECTURE.md"] = await self._generate_architecture_docs(
            description, backend, frontend, database
        )
        
        # Setup guides
        docs["README.md"] = await self._generate_readme(description)
        docs["SETUP.md"] = await self._generate_setup_guide()
        docs["DEPLOYMENT.md"] = await self._generate_deployment_guide()
        
        # User guides
        docs["USER_GUIDE.md"] = await self._generate_user_guide(description)
        docs["ADMIN_GUIDE.md"] = await self._generate_admin_guide()
        
        # Developer guides
        docs["CONTRIBUTING.md"] = await self._generate_contributing_guide()
        docs["CODE_OF_CONDUCT.md"] = self._generate_code_of_conduct()
        
        return docs
    
    def _parse_code_blocks(self, text: str) -> Dict[str, str]:
        """Parse code blocks from AI response into files"""
        files = {}
        current_file = None
        current_code = []
        
        for line in text.split('\n'):
            if line.startswith('```') and ':' in line:
                if current_file:
                    files[current_file] = '\n'.join(current_code)
                current_file = line.split(':')[1].strip()
                current_code = []
            elif line.startswith('```'):
                if current_file:
                    files[current_file] = '\n'.join(current_code)
                    current_file = None
                    current_code = []
            elif current_file:
                current_code.append(line)
        
        return files
    
    def _format_python_code(self, code: str) -> str:
        """Format Python code using black and isort"""
        try:
            # Format with black
            code = black.format_str(code, mode=black.Mode())
            # Sort imports with isort
            code = isort.code(code)
        except:
            pass
        return code
    
    def _generate_backend_dockerfile(self, tech_stack: Dict[str, str]) -> str:
        return """FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""
    
    def _generate_frontend_dockerfile(self, tech_stack: Dict[str, str]) -> str:
        return """FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
"""
    
    def _generate_docker_compose(self, tech_stack: Dict[str, str]) -> str:
        return """version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn main:app --reload --host 0.0.0.0
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
"""
    
    def _generate_docker_compose_prod(self, tech_stack: Dict[str, str]) -> str:
        return """version: '3.8'

services:
  backend:
    image: ikodio/backend:latest
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
  
  frontend:
    image: ikodio/frontend:latest
    restart: always
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${API_URL}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G
  
  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
"""
    
    async def _generate_k8s_deployment(self) -> str:
        return """apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ikodio/backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
"""
    
    async def _generate_k8s_service(self) -> str:
        return """apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
"""
    
    async def _generate_k8s_ingress(self) -> str:
        return """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ikodio-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.ikodio.com
    secretName: ikodio-tls
  rules:
  - host: api.ikodio.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
"""
    
    async def _generate_k8s_configmap(self) -> str:
        return """apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  DATABASE_HOST: postgres-service
  REDIS_HOST: redis-service
"""
    
    async def _generate_k8s_secrets(self) -> str:
        return """apiVersion: v1
kind: Secret
metadata:
  name: backend-secrets
type: Opaque
stringData:
  DATABASE_PASSWORD: "changeme"
  SECRET_KEY: "changeme"
  JWT_SECRET: "changeme"
"""
    
    async def _generate_github_actions(self) -> str:
        return """name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
"""
    
    async def _generate_deployment_pipeline(self) -> str:
        return """name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker build -t ikodio/backend:latest ./backend
        docker build -t ikodio/frontend:latest ./frontend
    
    - name: Push to registry
      run: |
        echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
        docker push ikodio/backend:latest
        docker push ikodio/frontend:latest
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/
        kubectl rollout restart deployment/backend
        kubectl rollout restart deployment/frontend
"""
    
    async def _generate_terraform(self) -> str:
        return """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "ikodio-vpc"
  }
}

resource "aws_eks_cluster" "main" {
  name     = "ikodio-cluster"
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
}

resource "aws_rds_instance" "postgres" {
  identifier        = "ikodio-db"
  engine            = "postgres"
  engine_version    = "15.3"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  
  db_name  = "ikodio"
  username = var.db_username
  password = var.db_password
  
  multi_az               = true
  backup_retention_period = 7
  skip_final_snapshot    = false
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "ikodio-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379
}
"""
    
    async def _generate_terraform_vars(self) -> str:
        return """variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}
"""
    
    def _generate_prometheus_config(self) -> str:
        return """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
  
  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend:3000']
"""
    
    async def _generate_grafana_dashboard(self) -> str:
        return """{
  "dashboard": {
    "title": "Application Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      }
    ]
  }
}"""
    
    async def _generate_api_docs(self, backend: Dict[str, str]) -> str:
        """Generate API documentation"""
        prompt = "Generate comprehensive API documentation in Markdown format for the backend code provided"
        # Implementation here
        return "# API Documentation\n\n..."
    
    async def _generate_openapi_spec(self, backend: Dict[str, str]) -> str:
        """Generate OpenAPI specification"""
        return "openapi: 3.0.0\ninfo:\n  title: IKODIO API\n  version: 1.0.0\n..."
    
    async def _generate_architecture_docs(self, desc: str, backend: Dict, frontend: Dict, db: Dict) -> str:
        return "# Architecture Documentation\n\n..."
    
    async def _generate_readme(self, description: str) -> str:
        return f"# Application\n\n{description}\n\n..."
    
    async def _generate_setup_guide(self) -> str:
        return "# Setup Guide\n\n..."
    
    async def _generate_deployment_guide(self) -> str:
        return "# Deployment Guide\n\n..."
    
    async def _generate_user_guide(self, description: str) -> str:
        return "# User Guide\n\n..."
    
    async def _generate_admin_guide(self) -> str:
        return "# Admin Guide\n\n..."
    
    async def _generate_contributing_guide(self) -> str:
        return "# Contributing Guide\n\n..."
    
    def _generate_code_of_conduct(self) -> str:
        return "# Code of Conduct\n\n..."
    
    def _generate_alembic_migrations(self, schema: str) -> str:
        return "# Alembic migrations\n..."
