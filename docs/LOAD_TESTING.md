# Load Testing Documentation

## Overview
Comprehensive load testing suite for IKODIO BugBounty platform using Locust.

## Test Scenarios

### 1. Smoke Test
- **Users**: 10
- **Spawn Rate**: 2 users/sec
- **Duration**: 2 minutes
- **Purpose**: Basic functionality verification
- **Command**: `./scripts/run-load-test.sh http://localhost:8000 smoke`

### 2. Load Test
- **Users**: 500 concurrent
- **Spawn Rate**: 25 users/sec
- **Duration**: 10 minutes
- **Purpose**: Normal traffic simulation
- **Command**: `./scripts/run-load-test.sh http://localhost:8000 load`

### 3. Stress Test
- **Users**: 1500 concurrent
- **Spawn Rate**: 100 users/sec
- **Duration**: 15 minutes
- **Purpose**: High load stress testing
- **Command**: `./scripts/run-load-test.sh http://localhost:8000 stress`

### 4. Spike Test
- **Users**: 2000 concurrent
- **Spawn Rate**: 200 users/sec
- **Duration**: 5 minutes
- **Purpose**: Sudden traffic spike simulation
- **Command**: `./scripts/run-load-test.sh http://localhost:8000 spike`

### 5. Endurance Test
- **Users**: 300 concurrent
- **Spawn Rate**: 10 users/sec
- **Duration**: 60 minutes
- **Purpose**: Long-term stability testing
- **Command**: `./scripts/run-load-test.sh http://localhost:8000 endurance`

### 6. Breakpoint Test
- **Users**: 5000 concurrent
- **Spawn Rate**: 500 users/sec
- **Duration**: 20 minutes
- **Purpose**: Find system breaking point
- **Command**: `./scripts/run-load-test.sh http://localhost:8000 breakpoint`

## User Types

### NormalUser (Weight: 10)
- **Wait Time**: 1-5 seconds
- **Tasks**: Bug reporting, scanning, analytics, marketplace
- **Behavior**: Regular user activity

### PowerUser (Weight: 3)
- **Wait Time**: 0.5-2 seconds
- **Tasks**: Intensive bug reporting and scanning
- **Behavior**: High activity power user

### AdminUser (Weight: 1)
- **Wait Time**: 2-8 seconds
- **Tasks**: Analytics, admin dashboard, system management
- **Behavior**: Administrative operations

### BurstTrafficUser (Weight: 2)
- **Wait Time**: 0.1-0.5 seconds
- **Tasks**: Rapid API requests
- **Behavior**: Burst traffic simulation

### DatabaseShardingTest (Weight: 2)
- **Tasks**: Cross-shard queries, shard-specific operations
- **Purpose**: Test database sharding performance

### ConcurrentScanTest (Weight: 3)
- **Tasks**: Multiple concurrent scans
- **Purpose**: Test scanning capacity under load

### RateLimitTest (Weight: 1)
- **Tasks**: Rapid requests to test rate limiting
- **Purpose**: Verify rate limiting implementation

### CacheEfficiencyTest (Weight: 2)
- **Tasks**: Cached vs non-cached requests
- **Purpose**: Test caching performance

## Task Sets

### AuthTaskSet
- Login
- Register
- Token refresh
- Logout

### BugReportTaskSet
- List bugs (pagination, filtering)
- Create bug reports
- Get bug details
- Update bug status
- Add comments

### ScanTaskSet
- List scans
- Create new scans
- Check scan status
- Retrieve scan results
- Cancel scans

### AnalyticsTaskSet
- Basic analytics
- Advanced analytics
- Analytics export (CSV/JSON/PDF)
- Dashboard metrics

### MarketplaceTaskSet
- Browse marketplace
- Search items
- Get item details
- Purchase flow

## Installation

```bash
# Install Locust
pip install locust locust-plugins

# Or use requirements file
pip install -r backend/requirements.txt
```

## Running Tests

### Interactive Mode (with Web UI)
```bash
cd /path/to/ikodio-bugbounty
locust -f backend/tests/load/test_scenarios.py --host=http://localhost:8000
# Open browser to http://localhost:8089
```

### Headless Mode (CLI)
```bash
# Using helper script
./scripts/run-load-test.sh http://localhost:8000 load

# Direct Locust command
locust -f backend/tests/load/test_scenarios.py \
    --host=http://localhost:8000 \
    --users=500 \
    --spawn-rate=25 \
    --run-time=10m \
    --headless \
    --html=results/report.html
```

### Testing Against Staging
```bash
./scripts/run-load-test.sh https://staging.ikodio.com load
```

### Testing Against Production
```bash
# Use with caution!
./scripts/run-load-test.sh https://api.ikodio.com smoke
```

## Performance Thresholds

### Response Times
- **95th percentile**: < 500ms
- **99th percentile**: < 1000ms
- **Median**: < 200ms
- **Max acceptable**: < 3000ms

### Error Rates
- **Target**: < 0.1% (1 in 1000 requests)
- **Warning**: > 0.5%
- **Critical**: > 1%

### Throughput
- **Minimum**: 100 requests/sec
- **Target**: 500 requests/sec
- **Peak**: 1000+ requests/sec

### Resource Utilization
- **CPU**: < 70% average
- **Memory**: < 80% usage
- **Database connections**: < 80% pool
- **Redis**: < 50% memory

## Results Analysis

### HTML Report
Generated at `monitoring/load-tests/results/{scenario}_{timestamp}/report.html`
- Request statistics
- Response time charts
- Failure analysis
- RPS (requests per second) graphs

### CSV Data
Files generated:
- `results_stats.csv` - Overall statistics
- `results_failures.csv` - Failed requests
- `results_stats_history.csv` - Time-series data

### Summary JSON
Contains:
- Test configuration
- Aggregated metrics
- Pass/fail status
- Timestamp

## Monitoring During Tests

### System Metrics
```bash
# CPU and Memory
htop

# Network
iftop

# Database
psql -U postgres -d ikodio -c "SELECT * FROM pg_stat_activity;"

# Redis
redis-cli INFO stats
```

### Application Logs
```bash
# Backend logs
tail -f backend/logs/app.log

# Access logs
tail -f nginx/logs/access.log

# Error logs
tail -f nginx/logs/error.log
```

### Grafana Dashboards
- Navigate to `http://localhost:3000`
- View real-time metrics during load tests
- Check system health indicators

## Common Issues

### 1. Connection Errors
**Symptom**: High connection failure rate
**Causes**:
- Backend not running
- Insufficient connection pool
- Network issues

**Solution**:
```python
# Increase connection pool in config.py
SQLALCHEMY_POOL_SIZE = 50
SQLALCHEMY_MAX_OVERFLOW = 100
```

### 2. Timeout Errors
**Symptom**: Request timeouts > 30s
**Causes**:
- Slow database queries
- Unoptimized endpoints
- Insufficient resources

**Solution**:
- Add database indexes
- Implement caching
- Scale infrastructure

### 3. Rate Limiting
**Symptom**: 429 errors
**Causes**:
- Rate limit exceeded

**Solution**:
- Adjust rate limits for testing
- Increase test user pool
- Distribute load

### 4. Memory Leaks
**Symptom**: Memory usage increasing over time
**Causes**:
- Unclosed connections
- Cache accumulation
- Memory leaks in code

**Solution**:
- Monitor with memory profiler
- Fix connection handling
- Implement cache eviction

## Best Practices

### Before Testing
1. Backup database
2. Clear logs
3. Reset Redis cache
4. Scale infrastructure if needed
5. Notify team about testing

### During Testing
1. Monitor system metrics
2. Watch error logs
3. Track database performance
4. Observe cache hit rates
5. Document anomalies

### After Testing
1. Analyze results
2. Compare with baselines
3. Document findings
4. Create optimization tickets
5. Update capacity planning

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Load Testing
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install locust
      - name: Run smoke test
        run: ./scripts/run-load-test.sh https://staging.ikodio.com smoke
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: load-test-results
          path: monitoring/load-tests/results/
```

## Scaling Recommendations

Based on load test results:

### < 100 RPS
- Single server sufficient
- PostgreSQL standalone
- Redis single instance

### 100-500 RPS
- 2-3 backend servers
- PostgreSQL with read replicas
- Redis with persistence

### 500-1000 RPS
- 5-10 backend servers (auto-scaling)
- PostgreSQL with sharding
- Redis cluster
- CDN for static assets

### > 1000 RPS
- 10+ backend servers (Kubernetes)
- Full database sharding
- Redis cluster with replication
- CDN + edge caching
- Load balancer with health checks

## Next Steps

1. Run smoke test to verify setup
2. Execute load test for baseline metrics
3. Analyze results and identify bottlenecks
4. Optimize slow endpoints
5. Re-test to verify improvements
6. Document capacity limits
7. Create monitoring alerts
8. Schedule regular load tests
