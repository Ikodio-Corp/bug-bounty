# Sentry Configuration for IKODIO BugBounty

## Overview

Sentry integration provides comprehensive error tracking, performance monitoring, and release management for the IKODIO BugBounty platform.

## Features

- Real-time error tracking and alerting
- Performance monitoring with transaction tracing
- User feedback collection
- Release tracking and deployment monitoring
- Breadcrumb tracking for context
- Integration with FastAPI, SQLAlchemy, Redis, and Celery
- Automatic PII filtering
- Custom context and tagging

## Setup

### 1. Install Dependencies

```bash
pip install sentry-sdk[fastapi]==1.40.0
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
ENVIRONMENT=production
RELEASE_VERSION=1.0.0
```

### 3. Start Sentry Service (Optional - Self-Hosted)

If using self-hosted Sentry:

```bash
cd monitoring/sentry
docker-compose up -d
```

Wait for services to start:

```bash
docker-compose ps
```

Access Sentry UI at http://localhost:9000

Initial setup:
1. Create admin account
2. Create organization
3. Create project
4. Copy DSN to `.env`

## Configuration

### Environment Variables

- `SENTRY_DSN`: Sentry Data Source Name (required)
- `SENTRY_TRACES_SAMPLE_RATE`: Transaction sampling rate (0.0-1.0, default: 0.1)
- `SENTRY_PROFILES_SAMPLE_RATE`: Profiling sampling rate (0.0-1.0, default: 0.1)
- `ENVIRONMENT`: Environment name (development/staging/production)
- `RELEASE_VERSION`: Application version for release tracking

### Integrations

Sentry automatically integrates with:

- **FastAPI**: HTTP request tracking, error capturing
- **SQLAlchemy**: Database query monitoring
- **Redis**: Cache operation tracking
- **Celery**: Async task monitoring
- **Logging**: Python logging integration

### Features

#### Error Tracking

All unhandled exceptions are automatically captured with:
- Full stack trace
- Request context (URL, method, headers)
- User information (if authenticated)
- Environment details
- Custom tags and contexts

#### Performance Monitoring

Transaction tracking for:
- HTTP requests (all endpoints)
- Database queries
- External API calls
- Cache operations
- Background tasks

#### User Context

Automatically sets user context on authenticated requests:
- User ID
- Email
- Username
- Subscription tier

#### Breadcrumbs

Automatically tracks:
- HTTP requests
- Database queries
- Cache operations
- Log messages
- Custom events

## Usage

### Automatic Tracking

Most errors and performance data are captured automatically through middleware.

### Manual Error Capture

```python
from integrations.sentry_client import sentry_service

try:
    risky_operation()
except Exception as e:
    sentry_service.capture_exception(
        e,
        tags={"operation": "risky_operation"},
        contexts={"custom": {"detail": "value"}}
    )
```

### Manual Message Capture

```python
sentry_service.capture_message(
    "Important event occurred",
    level="info",
    tags={"category": "business_logic"}
)
```

### Custom Breadcrumbs

```python
sentry_service.add_breadcrumb(
    message="User started scan",
    category="user_action",
    level="info",
    data={"scan_id": scan.id, "scan_type": scan.type}
)
```

### Transaction Tracking

```python
with sentry_service.start_transaction(name="complex_operation", op="custom") as transaction:
    with sentry_service.start_span(op="db.query", description="Fetch data"):
        data = await fetch_data()
    
    with sentry_service.start_span(op="processing", description="Process data"):
        result = process_data(data)
    
    return result
```

### User Context

```python
from integrations.sentry_client import sentry_service

sentry_service.set_user(current_user)
```

### Custom Context

```python
sentry_service.set_context("scan_context", {
    "scan_id": scan.id,
    "scan_type": scan.type,
    "target": scan.target
})
```

## Testing

### Test Endpoints (Development Only)

When `DEBUG=True`, test endpoints are available:

1. **Test Error**
```bash
curl -X POST http://localhost:8000/api/sentry/test-error \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. **Test Message**
```bash
curl -X POST http://localhost:8000/api/sentry/test-message \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **Test Transaction**
```bash
curl -X POST http://localhost:8000/api/sentry/test-transaction \
  -H "Authorization: Bearer YOUR_TOKEN"
```

4. **Test Feedback**
```bash
curl -X POST http://localhost:8000/api/sentry/capture-feedback \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "category": "feature_request",
    "message": "Great feature!"
  }'
```

5. **Health Check**
```bash
curl http://localhost:8000/api/sentry/health
```

## Monitoring

### Sentry Dashboard

Access your Sentry dashboard to view:

1. **Issues**: Grouped errors with frequency and impact
2. **Performance**: Transaction performance metrics
3. **Releases**: Deployment tracking and regression detection
4. **Alerts**: Configure alert rules for critical issues

### Key Metrics

Monitor these metrics in Sentry:

- Error rate and frequency
- Response time (p50, p95, p99)
- User impact (affected users)
- Release health (crash-free sessions)
- Performance regressions

### Alert Configuration

Set up alerts for:

- New error types
- Error rate spikes
- Performance degradation
- High-impact errors
- Specific error patterns

## Best Practices

1. **Sampling Rates**
   - Production: 0.1 (10%) for traces
   - Staging: 0.5 (50%) for traces
   - Development: 1.0 (100%) for traces

2. **PII Protection**
   - PII is automatically filtered
   - Avoid logging sensitive data in custom contexts
   - Review captured data regularly

3. **Context**
   - Add relevant context for debugging
   - Use structured data in contexts
   - Tag errors for easy filtering

4. **Releases**
   - Always set RELEASE_VERSION
   - Track deployments in Sentry
   - Use semantic versioning

5. **Performance**
   - Monitor transaction overhead
   - Adjust sampling rates based on volume
   - Use spans for detailed profiling

## Troubleshooting

### Sentry Not Capturing Errors

1. Check DSN configuration
2. Verify initialization in logs
3. Check sampling rates
4. Review before_send filters

### High Volume Issues

1. Reduce sampling rates
2. Add filters in before_send
3. Group similar errors
4. Increase rate limits

### Missing Context

1. Verify user context is set
2. Add custom contexts where needed
3. Check breadcrumb configuration
4. Review integration settings

## Integration with Other Services

### Kubernetes

Sentry is automatically configured in Kubernetes deployments through ConfigMap.

### Prometheus/Grafana

While Sentry handles errors, Prometheus/Grafana handle metrics:
- Use Prometheus for system metrics
- Use Grafana for visualization
- Use Sentry for error tracking
- Combine data for full observability

### ELK Stack

Sentry complements ELK:
- ELK: Application logs
- Sentry: Error tracking and performance
- Together: Complete observability

## Security

- DSN is sensitive, keep it secret
- Use environment variables, not code
- Review PII filtering regularly
- Rotate DSN if compromised
- Limit access to Sentry dashboard

## Cost Management

For Sentry SaaS:
- Monitor event quota
- Adjust sampling rates
- Filter low-value errors
- Use volume discounts
- Consider self-hosted for high volume

## Support

- Sentry Documentation: https://docs.sentry.io/
- Integration Issues: Check FastAPI integration docs
- Performance: Review performance monitoring guide
- Custom: Contact support for advanced features
