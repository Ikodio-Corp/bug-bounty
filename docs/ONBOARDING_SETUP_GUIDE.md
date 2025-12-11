# IKODIO Bug Bounty - Complete Onboarding & Setup Guide

**Last Updated:** December 11, 2025  
**Target Audience:** Yudha (DevOps/Data/Database) & Akmal (Development/Marketing)

---

## 🎯 Mission: Pure In-House Development
**ZERO third-party security tools** - We build everything from scratch:
- ❌ NO Burp Suite, OWASP ZAP, Nuclei
- ✅ YES Custom ML-powered vulnerability scanners
- ✅ YES Proprietary detection algorithms
- ✅ YES GPU-accelerated analysis

---

## 📦 Software Installation (Windows)

### 1. Essential Tools

**Git & Terminal:**
```powershell
# Git for Windows
winget install Git.Git

# Windows Terminal (Microsoft Store preferred)
winget install Microsoft.WindowsTerminal

# VS Code
winget install Microsoft.VisualStudioCode
```

**WSL2 Setup (WAJIB PERTAMA):**
```powershell
# Run PowerShell as Administrator
wsl --install -d Ubuntu-22.04
# Restart computer setelah ini
```

**Docker Desktop:**
```powershell
winget install Docker.DockerDesktop

# Setelah restart, enable WSL2 integration:
# Docker Desktop > Settings > Resources > WSL Integration
# Enable untuk Ubuntu-22.04
```

### 2. Programming Languages & Runtimes

**Python 3.11+ (Di WSL2 Ubuntu):**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install build dependencies untuk ML libraries
sudo apt install -y build-essential python3-dev \
  libssl-dev libffi-dev libxml2-dev libxslt1-dev \
  zlib1g-dev libjpeg-dev libpng-dev

# Verify
python3.11 --version
pip3 --version
```

**Node.js 18+ LTS:**
```bash
# Install Node.js di WSL2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version  # Should be v18.x.x
npm --version   # Should be 9.x.x
```

**PostgreSQL 15+:**
```bash
# Option 1: Docker (RECOMMENDED)
docker run -d \
  --name ikodio-postgres \
  -e POSTGRES_USER=ikodio \
  -e POSTGRES_PASSWORD=ikodio_secure_pass_2025 \
  -e POSTGRES_DB=ikodio_bugbounty \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15-alpine

# Option 2: Native Linux install di WSL2
sudo apt install -y postgresql-15 postgresql-contrib-15
```

**Redis 7:**
```bash
# Docker (RECOMMENDED)
docker run -d \
  --name ikodio-redis \
  -p 6379:6379 \
  -v redisdata:/data \
  redis:7-alpine redis-server --appendonly yes
```

### 3. Database Management Tools

**pgAdmin 4 (Windows):**
```powershell
winget install PostgreSQL.pgAdmin
```

**DBeaver (Universal DB Tool):**
```powershell
winget install dbeaver.dbeaver
```

**Redis Insight:**
- Download: https://redis.io/insight/
- Or Docker: `docker run -d -p 5540:5540 redis/redisinsight:latest`

### 4. DevOps Tools (Primarily for Yudha)

```bash
# kubectl (if using Kubernetes)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# AWS CLI (if using AWS)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Azure CLI (if using Azure)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Google Cloud SDK (if using GCP)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Postman (API Testing):**
```powershell
winget install Postman.Postman
```

### 5. GPU Workstation Tools (For ML Training)

**NVIDIA Drivers & CUDA (Di GPU Server/Workstation):**
```bash
# Check NVIDIA GPU
nvidia-smi

# Install NVIDIA Container Toolkit (untuk Docker GPU support)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

**CUDA Toolkit & cuDNN:**
```bash
# CUDA 12.0 (sesuaikan dengan GPU driver)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit-12-0

# Add to PATH
echo 'export PATH=/usr/local/cuda-12.0/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.0/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 6. ML & Data Science Tools

```bash
# Install Python ML libraries (akan diinstall via requirements.txt juga)
pip3 install --upgrade pip setuptools wheel

# Core ML libraries
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip3 install tensorflow-gpu  # if using TensorFlow
pip3 install onnx onnxruntime-gpu  # for optimized inference
pip3 install mlflow  # for model versioning
pip3 install dvc  # for data versioning

# Jupyter for experimentation
pip3 install jupyter jupyterlab ipython
```

---

## 🔧 VS Code Extensions (WAJIB)

### Core Extensions:
```
# Python Development
ms-python.python
ms-python.vscode-pylance
ms-python.black-formatter
ms-toolsai.jupyter

# Docker & Containers
ms-azuretools.vscode-docker
ms-vscode-remote.remote-wsl
ms-vscode-remote.remote-containers

# Git & Version Control
eamodio.gitlens
mhutchie.git-graph

# Database
ckolkman.vscode-postgres
mtxr.sqltools
mtxr.sqltools-driver-pg

# API Testing
rangav.vscode-thunder-client

# Code Quality
ms-python.isort
charliermarsh.ruff

# Frontend (Akmal)
dbaeumer.vscode-eslint
esbenp.prettier-vscode
bradlc.vscode-tailwindcss
dsznajder.es7-react-js-snippets

# DevOps (Yudha)
hashicorp.terraform
ms-kubernetes-tools.vscode-kubernetes-tools
redhat.vscode-yaml

# Misc
oderwat.indent-rainbow
usernamehw.errorlens
wayou.vscode-todo-highlight
```

**Install semua sekaligus:**
```bash
# Copy list extension IDs dan save ke file extensions.txt, lalu:
cat extensions.txt | xargs -L 1 code --install-extension
```

---

## 📁 Repository Setup

### 1. SSH Key Generation

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "yudha@ikodio.com"  # atau akmal@ikodio.com
ssh-keygen -t ed25519 -C "akmal@ikodio.com"

# Start SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Paste ke GitHub Settings > SSH and GPG keys > New SSH key
```

### 2. Git Configuration

```bash
# Global config
git config --global user.name "Yudha Firmansyah"  # atau "Akmal Gunawan"
git config --global user.email "yudha@ikodio.com"
git config --global core.editor "code --wait"
git config --global init.defaultBranch main
git config --global pull.rebase false

# Line endings (important untuk cross-platform)
git config --global core.autocrlf input  # Di WSL2/Linux
```

### 3. Clone Repositories

```bash
# Create workspace directory
mkdir -p ~/ikodio
cd ~/ikodio

# Clone main project
git clone git@github.com:ikodio/ikodio-bugbounty.git
cd ikodio-bugbounty

# Clone ML engine (separate repo)
cd ~/ikodio
git clone git@github.com:ikodio/ikodio-ml-engine.git

# Clone infrastructure configs (if exists)
git clone git@github.com:ikodio/ikodio-infrastructure.git
```

---

## ⚙️ Environment Configuration

### 1. Backend .env File

```bash
cd ~/ikodio/ikodio-bugbounty/backend
cp .env.example .env  # if exists
nano .env  # or code .env
```

**Complete .env template:**
```bash
# ============================================
# DATABASE
# ============================================
DATABASE_URL=postgresql://ikodio:ikodio_secure_pass_2025@localhost:5432/ikodio_bugbounty
DATABASE_TEST_URL=postgresql://ikodio:ikodio_secure_pass_2025@localhost:5432/ikodio_test
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_POOL_RECYCLE=3600

# ============================================
# REDIS CACHE
# ============================================
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600
REDIS_SESSION_TTL=86400

# ============================================
# ML ENGINE (GPU Workstation)
# ============================================
ML_ENGINE_URL=http://192.168.1.100:8003  # IP GPU server
ML_ENGINE_API_KEY=ml_engine_secret_key_2025
ML_ENGINE_TIMEOUT=300
ML_ENGINE_RETRY_ATTEMPTS=3

# ============================================
# SECURITY & AUTHENTICATION
# ============================================
SECRET_KEY=generate_with_openssl_rand_hex_32
JWT_SECRET_KEY=generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
PASSWORD_HASH_ALGORITHM=bcrypt
PASSWORD_MIN_LENGTH=12

# ============================================
# CORS & API
# ============================================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
API_V1_PREFIX=/api/v1
MAX_REQUEST_SIZE=10485760  # 10MB
RATE_LIMIT_PER_MINUTE=100

# ============================================
# EMAIL (SendGrid or AWS SES)
# ============================================
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xxxxx  # SendGrid API key
SMTP_FROM_EMAIL=noreply@ikodio.com
SMTP_FROM_NAME=IKODIO Bug Bounty

# ============================================
# PAYMENT (Stripe)
# ============================================
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# ============================================
# SCANNING (CUSTOM SCANNERS - NO THIRD PARTY)
# ============================================
# Custom scanner configs
SCANNER_MAX_THREADS=10
SCANNER_TIMEOUT=300
SCANNER_MAX_DEPTH=5
SCANNER_USER_AGENT=IKODIOScanner/1.0

# ML-powered scanning
ML_CONFIDENCE_THRESHOLD=0.75
ML_MODEL_VERSION=latest
ML_BATCH_SIZE=32

# ============================================
# CELERY (Background Tasks)
# ============================================
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_TIME_LIMIT=3600
CELERY_TASK_SOFT_TIME_LIMIT=3000

# ============================================
# MONITORING & LOGGING
# ============================================
LOG_LEVEL=INFO
SENTRY_DSN=https://xxx@sentry.io/xxx  # if using Sentry
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# ============================================
# CLOUD STORAGE (AWS S3 or MinIO)
# ============================================
S3_BUCKET_NAME=ikodio-bugbounty-dev
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAXXXXX
AWS_SECRET_ACCESS_KEY=xxxxx
# Or use MinIO for local development
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# ============================================
# FEATURE FLAGS
# ============================================
ENABLE_ML_PREDICTIONS=true
ENABLE_CUSTOM_SCANNERS=true
ENABLE_STRIPE_PAYMENTS=false  # Set true for production
ENABLE_EMAIL_NOTIFICATIONS=false  # Set true for production
MAINTENANCE_MODE=false

# ============================================
# DEVELOPMENT
# ============================================
DEBUG=true
ENVIRONMENT=development  # development, staging, production
```

**Generate secret keys:**
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32
```

### 2. Frontend .env File

```bash
cd ~/ikodio/ikodio-bugbounty/frontend
nano .env.local
```

```bash
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# ML Engine
NEXT_PUBLIC_ML_ENGINE_URL=http://localhost:8003

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx

# Analytics (optional)
NEXT_PUBLIC_GA_TRACKING_ID=G-XXXXXXXXXX
NEXT_PUBLIC_MIXPANEL_TOKEN=xxxxx

# Feature Flags
NEXT_PUBLIC_ENABLE_ML_FEATURES=true
NEXT_PUBLIC_ENABLE_PAYMENTS=false
```

### 3. ML Engine .env File

```bash
cd ~/ikodio/ikodio-ml-engine
nano .env
```

```bash
# GPU Configuration
CUDA_VISIBLE_DEVICES=0  # GPU 0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Model Configuration
MODEL_DIR=/app/models
MODEL_CACHE_DIR=/app/cache
MODEL_VERSION=1.0.0

# Training
BATCH_SIZE=32
LEARNING_RATE=0.001
MAX_EPOCHS=100
EARLY_STOPPING_PATIENCE=10

# Inference
INFERENCE_BATCH_SIZE=64
MAX_SEQUENCE_LENGTH=512
CONFIDENCE_THRESHOLD=0.75

# Data
TRAINING_DATA_DIR=/app/data/training
VALIDATION_SPLIT=0.2
TEST_SPLIT=0.1

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=ikodio-vulnerability-detection

# Redis for caching predictions
REDIS_URL=redis://localhost:6379/3
CACHE_TTL=3600
```

---

## 🚀 Initial Setup Steps

### Step 1: Verify WSL2 & Docker

```bash
# Check WSL version
wsl --list --verbose
# Ubuntu-22.04 should show "Running" with version 2

# Check Docker
docker --version
docker ps  # Should not show errors

# Test Docker GPU (jika ada GPU workstation)
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### Step 2: Backend Setup

```bash
cd ~/ikodio/ikodio-bugbounty/backend

# Create virtual environment
python3.11 -m venv venv

# Activate venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (for testing)
pip install -r requirements-dev.txt  # if exists

# Verify installation
python -c "import fastapi, sqlalchemy, redis, celery; print('All imports OK')"
```

### Step 3: Database Setup

```bash
# Create databases
docker exec -it ikodio-postgres psql -U ikodio -c "CREATE DATABASE ikodio_bugbounty;"
docker exec -it ikodio-postgres psql -U ikodio -c "CREATE DATABASE ikodio_test;"

# Run migrations
cd ~/ikodio/ikodio-bugbounty/backend
alembic upgrade head

# Verify
alembic current
# Should show latest migration
```

### Step 4: Frontend Setup

```bash
cd ~/ikodio/ikodio-bugbounty/frontend

# Install dependencies
npm install

# Verify
npm list --depth=0
```

### Step 5: ML Engine Setup

```bash
cd ~/ikodio/ikodio-ml-engine

# Option 1: Docker (RECOMMENDED)
docker-compose up -d

# Option 2: Local setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download pre-trained models (if any)
python scripts/download_models.py

# Verify
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
```

### Step 6: Start Services

```bash
# Terminal 1: Backend
cd ~/ikodio/ikodio-bugbounty/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd ~/ikodio/ikodio-bugbounty/frontend
npm run dev

# Terminal 3: Celery Worker
cd ~/ikodio/ikodio-bugbounty/backend
source venv/bin/activate
celery -A tasks.celery_app worker --loglevel=info

# Terminal 4: Celery Beat (scheduled tasks)
cd ~/ikodio/ikodio-bugbounty/backend
source venv/bin/activate
celery -A tasks.celery_app beat --loglevel=info

# Terminal 5: ML Engine
cd ~/ikodio/ikodio-ml-engine
docker-compose up  # or python -m uvicorn main:app --host 0.0.0.0 --port 8003
```

### Step 7: Verify Setup

**Backend Health Check:**
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

curl http://localhost:8000/api/v1/docs
# Should open API docs
```

**Frontend:**
```bash
# Open browser
http://localhost:3000
```

**ML Engine:**
```bash
curl http://localhost:8003/health
curl http://localhost:8003/api/v1/predict -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
```

**Database:**
```bash
docker exec -it ikodio-postgres psql -U ikodio -d ikodio_bugbounty -c "SELECT COUNT(*) FROM users;"
```

**Redis:**
```bash
docker exec -it ikodio-redis redis-cli PING
# Should return: PONG
```

---

## 📊 Monitoring Setup (Yudha)

### Prometheus & Grafana

```bash
cd ~/ikodio/ikodio-bugbounty/monitoring

# Start monitoring stack
docker-compose up -d

# Access:
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

**Import Grafana Dashboards:**
1. Login to Grafana (admin/admin)
2. Settings > Data Sources > Add Prometheus (http://prometheus:9090)
3. Dashboards > Import > Upload JSON files from `/monitoring/grafana/dashboards/`

---

## 🔥 Custom Scanner Setup (NO THIRD-PARTY)

### Install Scanner Dependencies

```bash
cd ~/ikodio/ikodio-bugbounty/backend

# Install additional scanning libraries
pip install aiohttp beautifulsoup4 lxml selenium playwright
pip install requests-html pyppeteer
pip install scapy dnspython

# Install Playwright browsers
playwright install chromium firefox

# Verify
python -c "from scanners.custom_scanner import CustomScanner; print('Scanner OK')"
```

### Download Vulnerability Databases

```bash
# CVE Database
cd ~/ikodio/ikodio-ml-engine/data
wget https://github.com/CVEProject/cvelistV5/archive/refs/heads/main.zip
unzip main.zip

# Exploit-DB
git clone https://gitlab.com/exploit-database/exploitdb.git

# CWE Database
wget https://cwe.mitre.org/data/xml/cwec_latest.xml.zip
unzip cwec_latest.xml.zip
```

---

## 🧪 Testing Setup

### Run Tests

```bash
# Backend tests
cd ~/ikodio/ikodio-bugbounty/backend
source venv/bin/activate
pytest tests/ -v --cov=. --cov-report=html

# Frontend tests
cd ~/ikodio/ikodio-bugbounty/frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 📚 Documentation to Read

### Priority 1 (Hari Pertama - WAJIB):
1. ✅ `docs/QUICKSTART.md` - Quick setup guide
2. ✅ `docs/PROJECT_STRUCTURE.txt` - Project structure overview  
3. ✅ `docs/PHASE6_IMPLEMENTATION_SUMMARY.md` - Latest implementation
4. ✅ `backend/README.md` - Backend API documentation
5. ✅ `docs/ONBOARDING_SETUP_GUIDE.md` - This file

### Priority 2 (Minggu Pertama):
1. `docs/ML_MODEL_DOCUMENTATION.md` - ML system architecture
2. `docs/IMPLEMENTATION_SUMMARY.md` - Full implementation details
3. `docs/API_ENDPOINT_INVENTORY.md` - All API endpoints
4. `docs/CUSTOM_SCANNER_ARCHITECTURE.md` - Scanner design (NEW)
5. `docs/DEPLOYMENT.md` - Deployment procedures

### Priority 3 (Minggu Kedua):
1. `docs/COMPREHENSIVE_STATUS_REPORT.md` - Project status
2. `docs/RBAC_IMPLEMENTATION.md` - Permissions system
3. `docs/SUBSCRIPTION_IMPLEMENTATION_COMPLETE.md` - Payment flows
4. `docs/AUDIT_REPORT_*.md` - Security audit reports

### External Resources:
- **FastAPI:** https://fastapi.tiangolo.com/
- **Next.js:** https://nextjs.org/docs
- **PostgreSQL:** https://www.postgresql.org/docs/15/
- **Redis:** https://redis.io/docs/
- **PyTorch:** https://pytorch.org/docs/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **Celery:** https://docs.celeryq.dev/

---

## 🐛 Troubleshooting

### Issue 1: Docker tidak bisa start
**Symptoms:** Docker Desktop stuck on "Starting..."

**Solutions:**
```powershell
# 1. Enable Virtualization di BIOS (AMD-V atau Intel VT-x)
# 2. Enable WSL2 feature
wsl --install
wsl --set-default-version 2

# 3. Enable Hyper-V (PowerShell as Admin)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# 4. Restart computer
shutdown /r /t 0
```

### Issue 2: Port sudah digunakan
**Symptoms:** "Address already in use"

**Solutions:**
```bash
# Check what's using port
netstat -ano | findstr :8000

# Kill process (PowerShell as Admin)
taskkill /PID <PID> /F

# Or change port di .env
PORT=8001
```

### Issue 3: Permission denied di WSL2
**Symptoms:** "Permission denied" saat run scripts

**Solutions:**
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/ikodio

# Make scripts executable
chmod +x scripts/*.sh
chmod +x deploy.sh

# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock
```

### Issue 4: Python package install error
**Symptoms:** "error: legacy-install-failure" atau "Failed building wheel"

**Solutions:**
```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install build dependencies
sudo apt install -y python3-dev build-essential libpq-dev

# Install with --no-binary for problematic packages
pip install --no-binary :all: psycopg2

# Or use binary version
pip install psycopg2-binary
```

### Issue 5: Node modules error
**Symptoms:** "MODULE_NOT_FOUND" atau weird build errors

**Solutions:**
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json .next

# Reinstall
npm install

# If still fails, use specific Node version
nvm install 18.18.0
nvm use 18.18.0
npm install
```

### Issue 6: Database connection error
**Symptoms:** "could not connect to server"

**Solutions:**
```bash
# Check if Postgres is running
docker ps | grep postgres

# Check logs
docker logs ikodio-postgres

# Test connection
psql postgresql://ikodio:ikodio_secure_pass_2025@localhost:5432/ikodio_bugbounty

# Restart container
docker restart ikodio-postgres
```

### Issue 7: GPU not detected
**Symptoms:** "CUDA not available" atau "No GPU found"

**Solutions:**
```bash
# Check NVIDIA driver
nvidia-smi

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test GPU in Docker
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### Issue 8: Celery worker not starting
**Symptoms:** "Consumer: Cannot connect to amqp://guest:**@127.0.0.1:5672//"

**Solutions:**
```bash
# Check Redis is running
docker ps | grep redis
docker logs ikodio-redis

# Test Redis connection
docker exec -it ikodio-redis redis-cli PING

# Fix Celery broker URL di .env
CELERY_BROKER_URL=redis://localhost:6379/1

# Restart worker
celery -A tasks.celery_app worker --loglevel=debug
```

### Issue 9: Migration errors
**Symptoms:** "Target database is not up to date"

**Solutions:**
```bash
# Check current migration
alembic current

# Check pending migrations
alembic history

# Stamp to specific version (CAREFUL!)
alembic stamp head

# Or downgrade and upgrade again
alembic downgrade -1
alembic upgrade head

# Generate new migration if schema changed
alembic revision --autogenerate -m "description"
```

### Issue 10: Frontend build errors
**Symptoms:** TypeScript errors atau "Module not found"

**Solutions:**
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall types
npm install --save-dev @types/react @types/node

# Fix TypeScript config
# Check tsconfig.json includes all necessary paths

# Restart dev server
npm run dev
```

---

## ✅ Setup Complete Checklist

### Infrastructure:
- [ ] WSL2 installed dan running (Ubuntu 22.04)
- [ ] Docker Desktop installed dan running
- [ ] Docker GPU support configured (if GPU available)
- [ ] PostgreSQL container running
- [ ] Redis container running

### Development Tools:
- [ ] Git installed dan configured
- [ ] SSH keys generated dan added to GitHub
- [ ] VS Code installed
- [ ] All VS Code extensions installed
- [ ] Postman atau Thunder Client installed

### Repositories:
- [ ] ikodio-bugbounty cloned
- [ ] ikodio-ml-engine cloned
- [ ] ikodio-infrastructure cloned (if exists)

### Backend:
- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] All Python dependencies installed
- [ ] .env file configured
- [ ] Database migrations run successfully
- [ ] Backend running at localhost:8000
- [ ] API docs accessible at localhost:8000/docs

### Frontend:
- [ ] Node.js 18+ installed
- [ ] NPM dependencies installed
- [ ] .env.local configured
- [ ] Frontend running at localhost:3000

### ML Engine:
- [ ] GPU drivers installed (if applicable)
- [ ] CUDA toolkit installed (if applicable)
- [ ] ML dependencies installed
- [ ] ML Engine running at localhost:8003

### Background Services:
- [ ] Celery worker running
- [ ] Celery beat scheduler running
- [ ] All workers healthy

### Testing:
- [ ] Backend tests passing (`pytest`)
- [ ] Frontend tests passing (`npm test`)
- [ ] Database accessible from test suite

### Monitoring (Yudha):
- [ ] Prometheus running at localhost:9090
- [ ] Grafana running at localhost:3000
- [ ] Dashboards imported

### Documentation:
- [ ] Read QUICKSTART.md
- [ ] Read PROJECT_STRUCTURE.txt
- [ ] Read relevant implementation docs
- [ ] Access to Slack/communication channels

### Access:
- [ ] GitHub access granted
- [ ] AWS/Azure access configured (if applicable)
- [ ] VPN configured (for staging/production)
- [ ] Credentials received dan saved securely

---

## 🎯 Next Steps After Setup

### For Yudha (DevOps/Data/Database):

**Week 1:**
1. ✅ Review database schema di `backend/models/`
2. ✅ Check indexes: `SELECT * FROM pg_indexes WHERE schemaname = 'public';`
3. ✅ Setup monitoring stack (Prometheus + Grafana)
4. ✅ Review CI/CD pipeline di `.github/workflows/`
5. ✅ Test backup script: `bash scripts/backup.sh`
6. ✅ Setup data versioning dengan DVC
7. ✅ Configure GPU workstation untuk ML training

**Week 2:**
1. Design ETL pipeline untuk CVE data ingestion
2. Implement custom scanner infrastructure
3. Setup automated model training pipeline
4. Configure Redis caching strategy
5. Review and optimize database queries

### For Akmal (Development/Marketing):

**Week 1:**
1. ✅ Review API endpoints di Postman
2. ✅ Import collection: `docs/postman_collection.json`
3. ✅ Run test suite: `pytest backend/tests/ -v`
4. ✅ Review frontend components di `frontend/app/` dan `frontend/components/`
5. ✅ Pick first task dari GitHub Issues
6. ✅ Implement first custom scanner (XSS detector)

**Week 2:**
1. Build ML integration UI components
2. Implement feedback mechanism
3. Create data labeling interface
4. Develop explainability visualizations
5. Start marketing landing pages

---

## 📞 Support & Communication

**Daily Standup:** 09:00 WIB (Zoom/Slack)
**Sprint Planning:** Monday 14:00 WIB
**Retrospective:** Friday 16:00 WIB

**Slack Channels:**
- `#general` - General discussion
- `#development` - Dev questions & updates
- `#devops` - Infrastructure & deployment
- `#ml-engine` - ML model discussions
- `#bugs` - Bug reports
- `#wins` - Celebrate achievements

**Emergency Contact:**
- CTO: +62-xxx-xxxx-xxxx (WhatsApp)
- Team Lead: Slack DM

---

## 🚨 Important Notes

1. **NEVER commit `.env` files** - They contain secrets
2. **NEVER push to main** - Always create feature branches
3. **ALWAYS write tests** - Target 80% coverage
4. **ALWAYS update documentation** - Keep README updated
5. **NO THIRD-PARTY SCANNERS** - Build everything in-house
6. **GPU Server = Production** - Handle with care
7. **Data is sacred** - Always backup before experiments

---

**Document Version:** 2.0  
**Last Updated:** December 11, 2025  
**Maintained by:** CTO (Hylmi Rafif Rabbani)
