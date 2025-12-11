# IKODIO ML Model Documentation

## Overview

The IKODIO Bug Bounty Platform uses machine learning models to automatically detect, classify, and prioritize security vulnerabilities. This document provides comprehensive information about the ML models, their architecture, performance characteristics, and operational guidelines.

## Model Architecture

### Primary Models

#### 1. Vulnerability Detection Model
- **Type**: XGBoost Binary Classifier
- **Purpose**: Determines if a reported issue is a valid vulnerability
- **Input Features**: 30 features including textual, behavioral, and technical indicators
- **Output**: Binary classification (vulnerability / not vulnerability) + confidence score
- **Accuracy**: 92.5% (on validation set)
- **Inference Time**: <100ms target, typically 45-65ms

#### 2. Severity Classification Model
- **Type**: Random Forest Multi-class Classifier  
- **Purpose**: Classifies vulnerability severity (Low, Medium, High, Critical)
- **Input Features**: Same 30 features + predicted vulnerability type
- **Output**: Severity level + confidence score
- **Accuracy**: 88.3% (on validation set)
- **Inference Time**: <50ms typically

#### 3. Vulnerability Type Classifier
- **Type**: XGBoost Multi-class Classifier
- **Purpose**: Identifies specific vulnerability type (SQL Injection, XSS, CSRF, etc.)
- **Input Features**: Enhanced feature set with pattern matching scores
- **Output**: Vulnerability type + confidence score
- **Accuracy**: 85.7% (on validation set)
- **Inference Time**: <60ms typically

## Feature Engineering

### Feature Categories

#### 1. Textual Features (10 features)
- `title_length`: Length of bug title (normalized)
- `description_length`: Length of bug description (normalized)
- `title_sentiment`: Sentiment analysis score (-1 to 1)
- `description_sentiment`: Sentiment analysis score (-1 to 1)
- `technical_detail_score`: Technical terminology density (0-1)
- `exploit_complexity`: Estimated exploit complexity (0-1)
- `has_proof`: Boolean - proof of concept provided
- `impact_score`: Estimated impact level (0-1)
- `keyword_match_score`: Security keyword matching score
- `language_quality`: Text quality assessment score

#### 2. Technical Features (12 features)
- `url`: Target URL (encoded)
- `endpoint_count`: Number of endpoints tested
- `parameter_count`: Number of parameters analyzed
- `has_headers`: Custom headers used
- `has_cookies`: Cookies involved
- `has_authentication`: Authentication required
- `has_ssl`: HTTPS connection
- `response_time_ms`: Response time measurement
- `status_code`: HTTP status code
- `content_type`: Response content type
- `response_size_bytes`: Response size
- `vulnerability_pattern_match`: Pattern matching result

#### 3. Behavioral Features (8 features)
- `reporter_reputation`: Reporter's historical accuracy (0-1)
- `asset_count`: Number of assets tested
- `severity`: Reported severity level
- `sql_injection_score`: SQL injection indicators (0-1)
- `xss_score`: XSS indicators (0-1)
- `csrf_score`: CSRF indicators (0-1)
- `idor_score`: IDOR indicators (0-1)
- `submission_hour`: Time of submission (normalized)

### Feature Preprocessing

```python
# Numerical features: StandardScaler normalization
scaler = StandardScaler()
numerical_features = ['title_length', 'description_length', 'response_time_ms', ...]
X_scaled = scaler.fit_transform(X[numerical_features])

# Categorical features: One-hot encoding
categorical_features = ['severity', 'content_type', ...]
X_encoded = pd.get_dummies(X[categorical_features])

# Text features: TF-IDF vectorization
tfidf = TfidfVectorizer(max_features=100)
X_text = tfidf.fit_transform(X['description'])
```

## Model Performance

### Accuracy Metrics

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| Vulnerability Detection | 92.5% | 91.3% | 93.8% | 92.5% | 0.95 |
| Severity Classification | 88.3% | 86.7% | 88.9% | 87.8% | 0.91 |
| Type Classification | 85.7% | 84.2% | 86.5% | 85.3% | 0.89 |

### Latency Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| P50 Latency | <50ms | 45ms |  PASS |
| P95 Latency | <100ms | 78ms |  PASS |
| P99 Latency | <150ms | 125ms |  PASS |
| Batch (32 items) | <500ms | 380ms |  PASS |

### Cache Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Cache Hit Rate | >70% | 82.5% |  PASS |
| Cache Latency | <5ms | 2.8ms |  PASS |
| Cache TTL | 1 hour | 3600s |  PASS |

## Operational Guidelines

### Model Training

#### Training Schedule
- **Full Retraining**: Daily at 2:00 AM UTC
- **Incremental Learning**: Hourly (on new feedback)
- **A/B Testing**: 7-day evaluation period
- **Model Rollout**: Gradual (10% → 50% → 100%)

#### Training Data Requirements
- **Minimum samples**: 1,000 labeled examples
- **Class balance**: 40-60% positive/negative ratio
- **Data freshness**: Maximum 30 days old
- **Validation split**: 20% held-out

#### Training Process
```bash
# Trigger manual training
python -m backend.tasks.ml_training_tasks.train_model \
  --model-type xgboost \
  --data-days 30 \
  --min-samples 1000

# Check training status
python -m backend.scripts.check_training_status
```

### Model Deployment

#### Deployment Checklist
1.  Model accuracy ≥ baseline - 2%
2.  Latency P95 < 100ms on test set
3.  No critical errors in evaluation
4.  A/B test shows improvement or parity
5.  Approval from 2 team members

#### Rollback Conditions (Automatic)
- Accuracy drops > 15% from baseline
- P95 latency exceeds 1000ms
- Error rate > 10%
- Circuit breaker opens

### Monitoring & Alerts

#### Key Metrics to Monitor
1. **Latency**: P50, P95, P99 inference time
2. **Throughput**: Predictions per second
3. **Accuracy**: Real-time feedback accuracy
4. **Cache**: Hit rate, miss rate
5. **Errors**: Error rate, error types
6. **Circuit Breaker**: Open/closed status

#### Alert Thresholds

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High Latency | P95 > 100ms for 5min | Warning | Investigate cache |
| Critical Latency | P95 > 200ms for 2min | Critical | Check ML engine |
| Low Cache Hit | <70% for 10min | Warning | Review cache strategy |
| High Error Rate | >5% for 5min | Warning | Check logs |
| Critical Errors | >10% for 2min | Critical | Engage on-call |
| Circuit Open | Breaker opens | Critical | Immediate response |
| Low Accuracy | <85% for 15min | Warning | Check model drift |

### Performance Optimization

#### Caching Strategy
```python
# Cache key generation (deterministic)
cache_key = md5(json.dumps(features, sort_keys=True))

# Cache TTL based on confidence
if confidence > 0.9:
    ttl = 3600  # 1 hour for high confidence
elif confidence > 0.7:
    ttl = 1800  # 30 minutes for medium confidence
else:
    ttl = 900   # 15 minutes for low confidence
```

#### Batch Optimization
```python
# Optimal batch size: 32 items
# Process multiple scans concurrently
batch_size = 32
max_concurrent_batches = 4

# Use asyncio for I/O-bound operations
results = await ml_prediction_optimizer.predict_batch_optimized(
    features_list,
    use_cache=True
)
```

#### Circuit Breaker Configuration
```python
# Circuit breaker settings
max_failures = 5          # Open after 5 consecutive failures
timeout = 300             # Reset after 5 minutes
half_open_requests = 3    # Test with 3 requests in half-open state
```

## API Usage

### Single Prediction
```python
POST /api/ml/predict
Content-Type: application/json

{
  "features": {
    "title_length": 45,
    "description_length": 320,
    "severity": "high",
    "has_proof": true,
    ...
  }
}

Response:
{
  "is_vulnerability": true,
  "vulnerability_type": "SQL Injection",
  "severity": 8.5,
  "confidence": 0.92,
  "inference_time_ms": 45.3,
  "cached": false,
  "model_version": "v2.3.1"
}
```

### Batch Prediction
```python
POST /api/ml/predict/batch
Content-Type: application/json

{
  "features_list": [
    { "title_length": 45, ... },
    { "title_length": 52, ... },
    ...
  ]
}

Response:
{
  "predictions": [
    { "is_vulnerability": true, ... },
    { "is_vulnerability": false, ... }
  ],
  "batch_size": 32,
  "total_time_ms": 380.5,
  "avg_time_per_item_ms": 11.9,
  "cached_count": 15
}
```

### Performance Stats
```python
GET /api/ml/performance/stats

Response:
{
  "cache_hit_rate": 82.5,
  "total_predictions": 15234,
  "avg_latency_ms": 45.2,
  "p95_latency_ms": 78.3,
  "error_rate": 0.012,
  "circuit_breaker_open": false
}
```

## Troubleshooting

### Common Issues

#### 1. High Latency
**Symptoms**: P95 latency > 100ms

**Possible Causes**:
- ML Engine overloaded
- Database connection pool exhausted
- Redis connection issues
- Network latency

**Solutions**:
1. Check ML Engine CPU/memory usage
2. Verify Redis connection: `redis-cli ping`
3. Check cache hit rate
4. Review Prometheus metrics
5. Consider horizontal scaling

#### 2. Low Cache Hit Rate
**Symptoms**: Cache hit rate < 70%

**Possible Causes**:
- Features not normalized consistently
- Cache TTL too short
- High feature variance
- Cache eviction too aggressive

**Solutions**:
1. Review feature preprocessing
2. Increase cache TTL for high-confidence predictions
3. Monitor cache memory usage
4. Implement cache warming strategy

#### 3. Circuit Breaker Opens
**Symptoms**: ml_circuit_breaker_status = 1

**Possible Causes**:
- ML Engine down
- Network connectivity issues
- ML Engine OOM
- Database connection failures

**Solutions**:
1. Check ML Engine health: `curl http://ml-engine:8003/health`
2. Review ML Engine logs
3. Restart ML Engine if necessary
4. Verify network connectivity
5. Check resource usage

#### 4. Model Accuracy Degradation
**Symptoms**: Feedback accuracy < 85%

**Possible Causes**:
- Data drift
- Feature distribution shift
- Model staleness
- Training data quality issues

**Solutions**:
1. Trigger manual retraining
2. Review recent feedback data
3. Check feature statistics
4. Validate training data quality
5. Consider model rollback

## Maintenance

### Weekly Tasks
- [ ] Review performance metrics dashboard
- [ ] Check training job success rate
- [ ] Analyze feedback accuracy trends
- [ ] Review alert history
- [ ] Update documentation if needed

### Monthly Tasks
- [ ] Comprehensive model evaluation
- [ ] Feature importance analysis
- [ ] A/B test results review
- [ ] Cache performance optimization
- [ ] Capacity planning review

### Quarterly Tasks
- [ ] Full model retraining with expanded dataset
- [ ] Feature engineering review and updates
- [ ] Model architecture evaluation
- [ ] Performance benchmark comparison
- [ ] Security audit of ML pipeline

## Version History

| Version | Date | Changes | Accuracy |
|---------|------|---------|----------|
| v2.3.1 | 2025-11-30 | Performance optimizations, batch support | 92.5% |
| v2.3.0 | 2025-11-25 | Auto-training, A/B testing | 92.1% |
| v2.2.0 | 2025-11-20 | Enhanced features, SHAP explanations | 91.8% |
| v2.1.0 | 2025-11-15 | Feedback integration | 91.2% |
| v2.0.0 | 2025-11-10 | Production release | 90.5% |

## Contact & Support

- **ML Team**: ml-team@ikodio.com
- **On-Call**: +1-555-ML-ONCALL
- **Slack**: #ml-support
- **Documentation**: https://docs.ikodio.com/ml
- **Runbook**: https://runbook.ikodio.com/ml

## References

- XGBoost Documentation: https://xgboost.readthedocs.io/
- Scikit-learn Documentation: https://scikit-learn.org/
- SHAP Documentation: https://shap.readthedocs.io/
- Prometheus Best Practices: https://prometheus.io/docs/practices/
- Internal ML Architecture: `docs/architecture/ml-system.md`
