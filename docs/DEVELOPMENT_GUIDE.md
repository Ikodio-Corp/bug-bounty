# Development Guide

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/ikodio/bugbounty.git
cd ikodio-bugbounty
```

2. Set up backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up frontend:
```bash
cd frontend
npm install
```

4. Configure environment variables:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# Edit .env files with your configuration
```

5. Initialize database:
```bash
cd backend
alembic upgrade head
python scripts/seed_data.py
```

6. Start services:
```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Redis
redis-server

# Terminal 4: Celery
cd backend
celery -A tasks.celery_app worker --loglevel=info
```

## Project Structure

### Backend
```
backend/
├── agents/          # AI agents for analysis
├── api/            # API routes
├── core/           # Core configuration
├── integrations/   # External integrations
├── middleware/     # Custom middleware
├── models/         # Database models
├── scanners/       # Security scanners
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── tasks/          # Celery tasks
├── tests/          # Unit tests
└── utils/          # Utility functions
```

### Frontend
```
frontend/
├── app/            # Next.js pages
├── components/     # React components
├── lib/            # Utilities
└── public/         # Static assets
```

## Development Workflow

### Adding New Features

1. Create feature branch:
```bash
git checkout -b feature/new-feature
```

2. Implement backend changes:
```python
# models/feature.py
from sqlalchemy import Column, Integer, String
from core.database import Base

class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

3. Create migration:
```bash
alembic revision --autogenerate -m "Add feature model"
alembic upgrade head
```

4. Add service layer:
```python
# services/feature_service.py
class FeatureService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_feature(self, data: dict):
        feature = Feature(**data)
        self.db.add(feature)
        self.db.commit()
        return feature
```

5. Create API endpoint:
```python
# api/routes/features.py
from fastapi import APIRouter, Depends
from services.feature_service import FeatureService

router = APIRouter()

@router.post("/features")
async def create_feature(data: dict, db: Session = Depends(get_db)):
    service = FeatureService(db)
    return service.create_feature(data)
```

6. Register route in main.py:
```python
from api.routes import features
app.include_router(features.router, prefix="/api", tags=["Features"])
```

7. Add tests:
```python
# tests/test_feature.py
def test_create_feature(db):
    service = FeatureService(db)
    feature = service.create_feature({"name": "Test"})
    assert feature.name == "Test"
```

8. Implement frontend:
```typescript
// app/features/page.tsx
'use client'
import { useState } from 'react'
import api from '@/lib/api'

export default function FeaturesPage() {
  const [features, setFeatures] = useState([])
  
  const createFeature = async (name: string) => {
    const response = await api.post('/features', { name })
    setFeatures([...features, response.data])
  }
  
  return <div>Feature UI</div>
}
```

### Code Style

#### Python
- Follow PEP 8
- Use type hints
- Max line length: 120
- Use docstrings for functions

```python
def calculate_score(bugs: List[Bug], severity_weights: Dict[str, float]) -> float:
    """
    Calculate reputation score based on bugs and severity weights.
    
    Args:
        bugs: List of bug objects
        severity_weights: Dictionary mapping severity to weight
    
    Returns:
        Calculated score as float
    """
    return sum(severity_weights.get(bug.severity, 1.0) for bug in bugs)
```

#### TypeScript
- Use functional components
- Prefer const over let
- Use TypeScript strict mode
- Define interfaces for props

```typescript
interface FeatureCardProps {
  title: string
  description: string
  onSelect: (id: number) => void
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, onSelect }) => {
  return (
    <div className="card" onClick={() => onSelect(1)}>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  )
}
```

## Testing Guidelines

### Unit Tests

Test individual functions and methods:

```python
def test_severity_score_calculation():
    assert calculate_severity_score("critical") == 10
    assert calculate_severity_score("high") == 7
    assert calculate_severity_score("medium") == 5
```

### Integration Tests

Test API endpoints:

```python
def test_create_bug_endpoint(client, auth_headers):
    response = client.post(
        "/api/bugs",
        json={"title": "Test", "severity": "high"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test"
```

### E2E Tests

Test complete user flows:

```typescript
test('user can submit bug report', async ({ page }) => {
  await page.goto('/bugs/new')
  await page.fill('[name="title"]', 'SQL Injection')
  await page.fill('[name="description"]', 'Found SQL injection...')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL(/\/bugs\/\d+/)
})
```

## Database Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "Description"
```

### Review Migration

Always review generated migrations before applying:

```python
def upgrade():
    op.add_column('users', sa.Column('new_field', sa.String(100)))

def downgrade():
    op.drop_column('users', 'new_field')
```

### Apply Migration

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1  # One step back
alembic downgrade base  # All the way back
```

## Performance Optimization

### Database Query Optimization

1. Use select_related/joinedload for relationships:
```python
users = db.query(User).options(joinedload(User.bugs)).all()
```

2. Add database indexes:
```python
class Bug(Base):
    target_domain = Column(String(255), index=True)
    created_at = Column(DateTime, index=True)
```

3. Use pagination:
```python
def get_bugs(page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    return db.query(Bug).offset(offset).limit(per_page).all()
```

### Caching

Use Redis for frequently accessed data:

```python
from core.redis import get_redis

redis_client = get_redis()

def get_platform_stats():
    cached = redis_client.get("platform_stats")
    if cached:
        return json.loads(cached)
    
    stats = calculate_stats()
    redis_client.setex("platform_stats", 300, json.dumps(stats))
    return stats
```

### Frontend Optimization

1. Use React.memo for expensive components
2. Implement lazy loading
3. Optimize images with Next.js Image
4. Use dynamic imports

```typescript
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <p>Loading...</p>
})
```

## Security Best Practices

### Input Validation

Always validate user input:

```python
from pydantic import BaseModel, validator

class BugCreate(BaseModel):
    title: str
    severity: str
    
    @validator('title')
    def title_length(cls, v):
        if len(v) < 5:
            raise ValueError('Title too short')
        return v
```

### SQL Injection Prevention

Use ORM queries, never string concatenation:

```python
# Good
bugs = db.query(Bug).filter(Bug.severity == severity).all()

# Bad - NEVER DO THIS
bugs = db.execute(f"SELECT * FROM bugs WHERE severity = '{severity}'")
```

### XSS Prevention

Sanitize user input in frontend:

```typescript
import DOMPurify from 'dompurify'

const sanitizedContent = DOMPurify.sanitize(userInput)
```

## Debugging

### Backend Debugging

Use Python debugger:

```python
import pdb; pdb.set_trace()
```

Or use logging:

```python
import logging
logger = logging.getLogger(__name__)
logger.info(f"Processing bug {bug_id}")
```

### Frontend Debugging

Use React DevTools and console:

```typescript
console.log('State:', state)
console.table(users)
```

## Contributing

1. Fork repository
2. Create feature branch
3. Write tests
4. Ensure all tests pass
5. Submit pull request

### Commit Messages

Follow conventional commits:

```
feat: Add bug export feature
fix: Resolve scan timeout issue
docs: Update API documentation
test: Add integration tests for admin
refactor: Simplify authentication logic
```

## Resources

- FastAPI Documentation: https://fastapi.tiangolo.com
- Next.js Documentation: https://nextjs.org/docs
- SQLAlchemy Documentation: https://docs.sqlalchemy.org
- PostgreSQL Documentation: https://www.postgresql.org/docs
