# 🚀 DEPLOYMENT CHECKLIST - Subscription System

## Pre-Deployment (30 minutes)

### 1. Environment Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Set `STRIPE_SECRET_KEY=sk_live_...`
- [ ] Set `STRIPE_WEBHOOK_SECRET=whsec_...`
- [ ] Set `STRIPE_PROFESSIONAL_PRICE_ID=price_...`
- [ ] Set `STRIPE_BUSINESS_PRICE_ID=price_...`
- [ ] Set `STRIPE_ENTERPRISE_PRICE_ID=price_...`
- [ ] Verify `DATABASE_URL` points to production database
- [ ] Set `ENVIRONMENT=production`

### 2. Database Backup (CRITICAL)
```bash
# Backup current database
pg_dump $DATABASE_URL > backup_pre_subscription_$(date +%Y%m%d_%H%M%S).sql

# Verify backup file exists and is not empty
ls -lh backup_pre_subscription_*.sql
```

### 3. Code Review
- [ ] All 11 files committed to git
- [ ] No `console.log()` or debug statements
- [ ] No hardcoded secrets or API keys
- [ ] Frontend environment variables set (`NEXT_PUBLIC_API_URL`)
- [ ] All tests passing (`pytest backend/tests/`)

---

## Deployment (15 minutes)

### Step 1: Database Migration
```bash
cd backend

# Check migration status
alembic current

# Review migration before running
cat database/migrations/add_usage_tracking.py

# Run migration (DRY RUN first if available)
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt *usage"
# Should show: scan_usage, autofix_usage, api_usage, storage_usage

# Verify existing users updated
psql $DATABASE_URL -c "SELECT subscription_tier, COUNT(*) FROM users GROUP BY subscription_tier"
# Should show only: FREE, PROFESSIONAL, BUSINESS, ENTERPRISE, GOVERNMENT
# NO: BRONZE, SILVER, GOLD, PLATINUM
```

** ROLLBACK IF ERRORS**:
```bash
# If migration fails, rollback immediately
alembic downgrade -1

# Restore from backup
psql $DATABASE_URL < backup_pre_subscription_*.sql
```

### Step 2: Backend Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Restart backend server
# (Method depends on your deployment - Docker, systemd, PM2, etc.)

# Docker example:
docker-compose restart backend

# Systemd example:
sudo systemctl restart ikodio-backend

# Verify backend is running
curl http://localhost:8002/health
# Should return: {"status": "healthy"}

# Test usage endpoint
curl http://localhost:8002/api/usage/summary \
  -H "Authorization: Bearer $TEST_TOKEN"
# Should return usage summary (not 404)
```

### Step 3: Frontend Deployment
```bash
cd frontend

# Install dependencies
npm install

# Build production bundle
npm run build

# Restart frontend server
# Docker example:
docker-compose restart frontend

# PM2 example:
pm2 restart ikodio-frontend

# Verify frontend is serving
curl http://localhost:3000
# Should return HTML (not error)

# Test pricing page
curl http://localhost:3000/pricing
# Should return HTML with 5 tier cards
```

---

## Post-Deployment Testing (10 minutes)

### Test 1: User Registration
```bash
# Register new user via API
curl -X POST http://localhost:8002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test-deploy@example.com",
    "password": "TestPass123!",
    "full_name": "Deploy Test",
    "subscription_tier": "FREE"
  }'

# Should return: {"access_token": "...", "user": {...}}
# Save token for next tests
```

### Test 2: Scan Limit Enforcement
```bash
# Set token from above
TOKEN="..."

# Try to start scan (should work for first 10)
for i in {1..11}; do
  echo "Scan $i:"
  curl -X POST http://localhost:8002/api/scans/start \
    -H "Authorization: Bearer $TOKEN"
  echo ""
done

# Scan 1-10: Should return {"scan_id": ..., "scans_remaining": ...}
# Scan 11: Should return HTTP 402 with upgrade prompt
```

### Test 3: Usage API
```bash
# Get usage summary
curl http://localhost:8002/api/usage/summary \
  -H "Authorization: Bearer $TOKEN"

# Should return:
# {
#   "scans": {"current": 10, "limit": 10, "remaining": 0},
#   "warnings": [{"type": "scans", "message": "..."}]
# }
```

### Test 4: Frontend Pages
- [ ] Open browser to `http://your-domain.com/login`
  - Should see beautiful glassmorphism login page (not redirect)
- [ ] Navigate to `/register`
  - Should see register form with company field
- [ ] Navigate to `/pricing`
  - Should see 5 tier cards with gradients and animations
- [ ] Try to start scan as Free user after limit
  - Should see UpgradePrompt modal (not just error message)

---

## Monitoring Setup (5 minutes)

### 1. Database Monitoring
```sql
-- Create view for subscription metrics
CREATE VIEW subscription_metrics AS
SELECT 
  subscription_tier,
  COUNT(*) as user_count,
  COUNT(*) FILTER (WHERE subscription_status = 'active') as active_count,
  COUNT(*) FILTER (WHERE subscription_status = 'trial') as trial_count,
  AVG(EXTRACT(EPOCH FROM (subscription_end_date - NOW())) / 86400) as avg_days_remaining
FROM users
GROUP BY subscription_tier;

-- Query anytime:
SELECT * FROM subscription_metrics;
```

### 2. Usage Monitoring
```sql
-- Create view for usage statistics
CREATE VIEW usage_statistics AS
SELECT 
  u.subscription_tier,
  COUNT(DISTINCT su.user_id) as users_with_scans,
  SUM(su.scan_count) as total_scans,
  AVG(su.scan_count) as avg_scans_per_user,
  MAX(su.scan_count) as max_scans_by_user
FROM users u
LEFT JOIN scan_usage su ON u.id = su.user_id
WHERE su.month = TO_CHAR(NOW(), 'YYYY-MM')
GROUP BY u.subscription_tier;

-- Query anytime:
SELECT * FROM usage_statistics;
```

### 3. Application Logs
```bash
# Set up log monitoring for key events
grep "SubscriptionLimitError" /var/log/ikodio/backend.log | tail -20
grep "subscription_upgraded" /var/log/ikodio/backend.log | tail -20
grep "trial_started" /var/log/ikodio/backend.log | tail -20
```

### 4. Alerts
Set up alerts for:
- [ ] Database migration failures
- [ ] HTTP 500 errors on usage endpoints
- [ ] Stripe webhook failures
- [ ] Sudden drop in registrations
- [ ] High number of HTTP 402 responses (good signal!)

---

## Rollback Plan (If Issues Found)

### Immediate Rollback (< 5 minutes)
```bash
# 1. Stop accepting new traffic
# (Method depends on load balancer - e.g., switch to maintenance mode)

# 2. Rollback database
alembic downgrade -1

# OR restore from backup:
psql $DATABASE_URL < backup_pre_subscription_*.sql

# 3. Deploy previous backend version
git checkout <previous-commit>
docker-compose restart backend

# 4. Deploy previous frontend version
cd frontend
git checkout <previous-commit>
npm run build
pm2 restart ikodio-frontend

# 5. Verify rollback successful
curl http://localhost:8002/health
curl http://localhost:3000

# 6. Resume traffic
```

### Partial Rollback (Keep Some Features)
If only frontend has issues:
```bash
# Rollback frontend only
cd frontend
git checkout <previous-commit>
npm run build
pm2 restart ikodio-frontend

# Backend remains updated (usage tracking still works via API)
```

If only backend has issues:
```bash
# Rollback backend only
cd backend
git checkout <previous-commit>
alembic downgrade -1
docker-compose restart backend

# Frontend can show "Feature coming soon" message
```

---

## Success Criteria

### Must Pass Before Considering Deployment Successful:
- [x] All 4 usage tables exist in database
- [x] No BRONZE/SILVER/GOLD/PLATINUM users remain
- [x] Backend `/health` endpoint returns 200
- [x] Backend `/api/usage/summary` returns 200 (not 404)
- [x] Frontend `/login` shows new login page (not redirect)
- [x] Frontend `/register` shows new register page
- [x] Frontend `/pricing` shows 5 tier cards
- [x] Scan limit enforcement works (HTTP 402 on limit)
- [x] UpgradePrompt modal appears on limit
- [x] No server errors in logs (500s)
- [x] Database backup created and verified

### Good to Have (Monitor for First 24 Hours):
- [ ] 10+ new user registrations
- [ ] 1+ user hits scan limit and sees upgrade prompt
- [ ] 0 critical bugs reported
- [ ] Average response time < 500ms for usage endpoints
- [ ] Database query performance acceptable (< 100ms)

---

## Communication Plan

### Before Deployment
**To Team**:
```
🚀 Deployment Notice: Subscription System

**When**: Today at 2:00 PM UTC
**Duration**: ~30 minutes maintenance window
**Impact**: Brief downtime (5-10 min), then full functionality restored

**What's New**:
- 5-tier subscription system (FREE, PROFESSIONAL, BUSINESS, ENTERPRISE, GOVERNMENT)
- Usage tracking for scans, auto-fixes, API requests
- Beautiful new login/register pages
- Pricing page with tier comparison

**What to Watch**:
- User registrations continue working
- No errors in logs
- Upgrade prompts appear when limits hit

**Rollback Plan**: Available if critical issues found
```

### After Deployment
**To Team** (if successful):
```
 Deployment Complete: Subscription System Live

**Status**: All systems operational
**Tests**:  Passed
**New Features**: Live and working
**Monitoring**: Active

**Next Steps**:
- Monitor user feedback
- Track conversion metrics
- Optimize upgrade flow based on data

**Known Issues**: None
```

**To Users** (email/announcement):
```
🎉 Introducing IKODIO Subscription Plans!

We've launched flexible pricing to better serve your needs:

�� What's New:
- FREE Plan: 10 scans/month forever
- PROFESSIONAL: 100 scans + AI features (Rp 450K/mo)
- BUSINESS: 300 scans + team features (Rp 1.5M/mo)
- ENTERPRISE: Unlimited everything (Rp 10M/mo)

🎁 Special Launch Offer:
- 14-day FREE trial for Professional tier
- No credit card required to start

👉 Explore Plans: https://ikodio.com/pricing

Questions? Reply to this email or visit our Help Center.

- The IKODIO Team
```

---

## Post-Deployment Tasks (First Week)

### Day 1
- [ ] Monitor error rates (should be < 1%)
- [ ] Check database performance
- [ ] Review first user registrations
- [ ] Verify Stripe webhooks working (if integrated)
- [ ] Check for any UX issues reported

### Day 2-3
- [ ] Analyze upgrade prompt impressions vs clicks
- [ ] Review user feedback
- [ ] Identify any edge cases
- [ ] Optimize slow queries if found

### Day 4-7
- [ ] Calculate initial conversion rates
- [ ] A/B test upgrade prompt messaging (if needed)
- [ ] Implement usage dashboard UI (next priority)
- [ ] Plan next iteration improvements

---

## Emergency Contacts

**On-Call Engineer**: [Your contact]  
**Database Admin**: [DBA contact]  
**DevOps Lead**: [DevOps contact]  
**Stripe Support**: https://support.stripe.com  

**Escalation Path**:
1. Check logs and metrics
2. Attempt automatic fix (restart services)
3. Manual rollback if automatic fix fails
4. Contact on-call engineer if rollback fails
5. Escalate to database admin if data corruption suspected

---

## Appendix: Quick Commands

### Check System Status
```bash
# Backend health
curl http://localhost:8002/health

# Database connection
psql $DATABASE_URL -c "SELECT 1"

# Redis connection
redis-cli ping

# Frontend serving
curl -I http://localhost:3000
```

### Check Subscription Stats
```bash
# User count by tier
psql $DATABASE_URL -c "
SELECT subscription_tier, COUNT(*) 
FROM users 
GROUP BY subscription_tier
"

# Active trials
psql $DATABASE_URL -c "
SELECT COUNT(*) 
FROM users 
WHERE subscription_status = 'trial'
AND subscription_end_date > NOW()
"

# Users near scan limit (>80%)
psql $DATABASE_URL -c "
SELECT u.email, su.scan_count, su.limit 
FROM users u
JOIN scan_usage su ON u.id = su.user_id
WHERE su.month = TO_CHAR(NOW(), 'YYYY-MM')
AND su.scan_count::float / su.limit > 0.8
LIMIT 10
"
```

---

**Deployment Lead**: _______________  
**Date Deployed**: _______________  
**Rollback Needed**: [ ] Yes [ ] No  
**Issues Found**: _______________  
**Resolution**: _______________  

**Sign-off**: All checklist items completed 
