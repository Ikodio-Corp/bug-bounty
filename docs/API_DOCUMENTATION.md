# IKODIO BugBounty - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [Authentication](#authentication)
5. [WebSocket Integration](#websocket-integration)
6. [Admin Features](#admin-features)
7. [Integrations](#integrations)
8. [Testing](#testing)

## Overview

IKODIO BugBounty is an enterprise-grade AI-powered vulnerability detection and bug bounty platform. The platform combines automated security scanning, AI-powered analysis, and a comprehensive bug bounty marketplace.

### Key Features
- AI-powered vulnerability detection
- Multiple scanner integrations (Nuclei, ZAP, Burp Suite)
- Real-time WebSocket notifications
- Advanced analytics and reporting
- Bug marketplace and trading
- Guild system for collaboration
- NFT tokenization of discoveries
- Comprehensive admin dashboard
- External platform integrations

## Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for sessions and real-time data
- **Task Queue**: Celery with Redis broker
- **Authentication**: JWT with OAuth2, 2FA, SAML 2.0
- **WebSocket**: FastAPI WebSocket support

### Frontend Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **API Client**: Axios

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes with Helm charts
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **Error Tracking**: Sentry
- **CI/CD**: GitHub Actions, GitLab CI

## API Reference

### Base URL
```
Production: https://api.ikodio.com
Development: http://localhost:8000
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secretpass
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Scan Endpoints

#### Create Scan
```http
POST /api/scans
Authorization: Bearer <token>
Content-Type: application/json

{
  "target_url": "https://example.com",
  "scan_type": "full",
  "scanner": "nuclei"
}
```

#### Get Scan Status
```http
GET /api/scans/{scan_id}
Authorization: Bearer <token>
```

#### List User Scans
```http
GET /api/scans?page=1&per_page=20
Authorization: Bearer <token>
```

### Bug Endpoints

#### Submit Bug
```http
POST /api/bugs
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "SQL Injection in login form",
  "description": "Detailed description...",
  "bug_type": "sql_injection",
  "severity": "high",
  "target_url": "https://example.com/login",
  "target_domain": "example.com",
  "steps_to_reproduce": "Steps...",
  "proof_of_concept": "POC..."
}
```

#### List Bugs
```http
GET /api/bugs?page=1&severity=high&validated=true
Authorization: Bearer <token>
```

#### Get Bug Details
```http
GET /api/bugs/{bug_id}
Authorization: Bearer <token>
```

### Admin Endpoints

#### Platform Overview
```http
GET /api/admin/overview
Authorization: Bearer <admin_token>
```

Response:
```json
{
  "users": {
    "total": 1500,
    "active": 1200,
    "inactive": 300
  },
  "bugs": {
    "total": 5000,
    "pending": 150,
    "validated": 4500,
    "rejected": 350
  },
  "scans": {
    "total": 10000,
    "active": 50,
    "completed": 9950
  },
  "revenue": {
    "total": 2500000,
    "this_month": 185000
  }
}
```

#### Manage Users
```http
GET /api/admin/users?page=1&role=hunter&status=active
PUT /api/admin/users/{user_id}/status
DELETE /api/admin/users/{user_id}
```

#### Moderate Bugs
```http
GET /api/admin/bugs?status=pending&severity=critical
POST /api/admin/bugs/{bug_id}/validate
POST /api/admin/bugs/{bug_id}/reject
```

### Integration Endpoints

#### Sync to Jira
```http
POST /api/integrations/jira/sync
Authorization: Bearer <token>
Content-Type: application/json

{
  "bug_id": 123,
  "project_key": "SEC",
  "issue_type": "Bug"
}
```

#### Sync to Linear
```http
POST /api/integrations/linear/sync
Authorization: Bearer <token>
Content-Type: application/json

{
  "bug_id": 123,
  "team_id": "team_abc123"
}
```

## Authentication

### JWT Token Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Two-Factor Authentication

Enable 2FA:
```http
POST /api/auth/2fa/enable
Authorization: Bearer <token>
```

Verify 2FA:
```http
POST /api/auth/2fa/verify
Content-Type: application/json

{
  "code": "123456"
}
```

### OAuth2 Integration

Supported providers: Google, GitHub, GitLab

```http
GET /api/auth/oauth/{provider}
GET /api/auth/oauth/{provider}/callback?code=...
```

## WebSocket Integration

### Connection

Connect to WebSocket with JWT token:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/YOUR_TOKEN')

ws.onopen = () => {
  console.log('Connected')
}

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('Message:', data)
}
```

### Subscribe to Scan Updates

```javascript
ws.send(JSON.stringify({
  type: 'subscribe_scan',
  scan_id: 123
}))
```

### Join Guild Channel

```javascript
ws.send(JSON.stringify({
  type: 'join_guild',
  guild_id: 456
}))
```

### Send Guild Message

```javascript
ws.send(JSON.stringify({
  type: 'guild_message',
  guild_id: 456,
  message: 'Hello team!'
}))
```

## Admin Features

### User Management
- View all users with filters (role, status)
- Activate/deactivate accounts
- Change user roles
- Delete users
- View user statistics

### Bug Moderation
- Review pending bugs
- Validate bugs and set bounties
- Reject bugs with reasons
- Filter by severity and status
- Track payment status

### Scan Monitoring
- Monitor active scans
- View scan progress
- Filter by status
- Track vulnerabilities found

### Analytics Dashboard
- Platform-wide statistics
- Daily trends
- User growth metrics
- Bug submission trends
- Revenue tracking

## Integrations

### Issue Tracking

#### Jira
```python
# Configure in .env
JIRA_API_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your_api_token
```

#### Linear
```python
LINEAR_API_TOKEN=your_api_token
```

### Bug Bounty Platforms

#### HackerOne
```python
HACKERONE_API_TOKEN=your_api_token
```

#### Bugcrowd
```python
BUGCROWD_API_TOKEN=your_api_token
```

### Cloud Providers

#### AWS Security Hub
```python
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

## Testing

### Backend Tests

Run all tests:
```bash
cd backend
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_admin_service.py
```

### Frontend Tests

Run unit tests:
```bash
cd frontend
npm test
```

Run with coverage:
```bash
npm test -- --coverage
```

Run E2E tests:
```bash
npx playwright test
```

### Linting

Backend:
```bash
flake8 . --max-line-length=120
```

Frontend:
```bash
npm run lint
```

Type checking:
```bash
npm run type-check
```

## Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/ikodio
POSTGRES_USER=ikodio
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=ikodio_bugbounty

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Integrations
JIRA_API_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your_token
LINEAR_API_TOKEN=your_token
HACKERONE_API_TOKEN=your_token
BUGCROWD_API_TOKEN=your_token
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Deployment

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes

```bash
helm install ikodio ./helm/ikodio-bugbounty
```

### Manual Deployment

Backend:
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run build
npm start
```

## Rate Limiting

Default rate limits:
- Authentication: 5 requests per minute
- API endpoints: 100 requests per minute
- WebSocket: 1000 messages per minute

## Error Codes

- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `429`: Too Many Requests
- `500`: Internal Server Error

## Support

- Documentation: https://docs.ikodio.com
- API Status: https://status.ikodio.com
- Email: support@ikodio.com
- GitHub: https://github.com/ikodio/bugbounty

## License

Proprietary - All Rights Reserved
