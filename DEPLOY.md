# Deployment Guide - Strix AI Pentest Web Interface

## Railway Deployment (Recommended)

### Option 1: One-Click Deploy

1. Click the "Deploy on Railway" button in README.md
2. Connect your GitHub account
3. Set environment variables:
   - `ANTHROPIC_API_KEY` - Your Claude API key from https://console.anthropic.com
4. Click "Deploy"
5. Wait 3-5 minutes for build and deployment
6. Access your app at the generated Railway URL

### Option 2: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing project or create new
railway link

# Set environment variables
railway variables set ANTHROPIC_API_KEY=sk-ant-api03-...

# Deploy
railway up

# Open in browser
railway open
```

### Required Environment Variables on Railway

```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Optional Environment Variables

```env
STRIX_LLM=anthropic/claude-sonnet-4-20250514
SECRET_KEY=your-random-secret-key
DEBUG=false
```

## GitHub Integration

### Push to GitHub

```bash
# Initialize git repository
cd strix-railway
git init
git add .
git commit -m "Initial commit - Strix AI Pentest Web Interface"

# Create GitHub repository at https://github.com/new
# Then push:
git remote add origin https://github.com/yourusername/strix-railway.git
git branch -M main
git push -u origin main
```

### Connect Railway to GitHub

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Dockerfile
6. Set environment variables
7. Deploy

### Auto-Deploy on Push

Railway automatically deploys when you push to main branch:

```bash
# Make changes
vim app.py

# Commit and push
git add .
git commit -m "Update: improved scan performance"
git push origin main

# Railway deploys automatically
```

## Alternative Deployment Options

### Docker Hub + Railway

```bash
# Build and push to Docker Hub
docker build -t yourusername/strix-railway:latest .
docker push yourusername/strix-railway:latest

# Deploy on Railway using Docker Hub image
# In Railway dashboard:
# 1. New Project → Deploy Docker Image
# 2. Enter: yourusername/strix-railway:latest
# 3. Set environment variables
# 4. Deploy
```

### Render.com

```yaml
# render.yaml
services:
  - type: web
    name: strix-pentest
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: PORT
        value: 8080
```

Deploy:
```bash
# Connect repo to Render
# Blueprint will be auto-detected
```

### Heroku

```bash
# Install Heroku CLI
brew tap heroku/brew && brew install heroku

# Login
heroku login

# Create app
heroku create strix-pentest

# Set buildpack
heroku stack:set container

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=sk-ant-api03-...

# Deploy
git push heroku main

# Open
heroku open
```

### DigitalOcean App Platform

```yaml
# .do/app.yaml
name: strix-pentest
services:
  - name: web
    dockerfile_path: Dockerfile
    github:
      repo: yourusername/strix-railway
      branch: main
    envs:
      - key: ANTHROPIC_API_KEY
        scope: RUN_TIME
        type: SECRET
    http_port: 8080
    instance_size_slug: basic-xxs
    instance_count: 1
```

## Local Testing Before Deploy

### Test with Docker Compose

```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-api03-...

# Build and run
docker-compose up --build

# Test in browser
open http://localhost:8080

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### Test with Python directly

```bash
# Install dependencies
pip install -r requirements.txt
pip install strix-agent

# Set environment variables
export ANTHROPIC_API_KEY=sk-ant-api03-...
export STRIX_LLM=anthropic/claude-sonnet-4-20250514
export PORT=8080

# Run
python app.py

# Test
curl http://localhost:8080/health
```

## Post-Deployment Checks

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "strix_installed": true,
  "claude_available": true,
  "active_scans": 0
}
```

### 2. Test Scan
```bash
curl -X POST https://your-app.railway.app/api/scan/start \
  -H "Content-Type: application/json" \
  -d '{
    "target": "https://example.com",
    "scan_type": "web",
    "depth": 2
  }'
```

### 3. Check Logs
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Docker
docker logs -f strix-railway-strix-web-1
```

## Troubleshooting

### Build fails with "Docker not found"
- Railway doesn't provide Docker-in-Docker
- Solution: Use Railway's Docker service or run Strix without Docker sandbox

### "ANTHROPIC_API_KEY not set"
```bash
# Check variable is set
railway variables

# Set it
railway variables set ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Port binding error
- Railway automatically sets `PORT` environment variable
- Ensure app uses `PORT` from environment: `int(os.environ.get('PORT', 8080))`

### Out of memory
- Increase Railway instance size
- Or optimize by reducing worker count in gunicorn

### Scan timeout
- Increase timeout in `app.py`:
  ```python
  process.communicate(timeout=7200)  # 2 hours
  ```

## Security Hardening for Production

### 1. Add Authentication

```python
# app.py
from functools import wraps
from flask import request, abort

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or auth != f"Bearer {os.environ.get('API_TOKEN')}":
            abort(401)
        return f(*args, **kwargs)
    return decorated

@app.route('/api/scan/start', methods=['POST'])
@require_auth
def start_scan():
    # ... existing code
```

Set API_TOKEN on Railway:
```bash
railway variables set API_TOKEN=$(openssl rand -hex 32)
```

### 2. Rate Limiting

```bash
pip install flask-limiter

# app.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/scan/start', methods=['POST'])
@limiter.limit("10 per hour")
def start_scan():
    # ... existing code
```

### 3. HTTPS Only

```python
# app.py
@app.before_request
def force_https():
    if not request.is_secure and os.environ.get('ENV') == 'production':
        return redirect(request.url.replace('http://', 'https://'), code=301)
```

### 4. Input Validation

```python
from urllib.parse import urlparse

def validate_target(target: str) -> bool:
    if target.startswith('http'):
        parsed = urlparse(target)
        # Block internal/private IPs
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False
    return True
```

## Cost Optimization

### Railway Free Tier
- 500 hours/month free
- $5 credit
- Sleep after 30 min inactivity

### Claude API Costs
- Sonnet 4: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Estimate: $0.10 - $1.00 per full pentest scan

### Tips
1. Use scan depth wisely (lower = cheaper)
2. Implement caching for repeated targets
3. Set max concurrent scans limit
4. Monitor usage in Anthropic console

## Monitoring

### Railway Dashboard
- CPU/Memory usage
- Request logs
- Error tracking

### Custom Monitoring

```python
# app.py
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Metrics available at /metrics
```

## Support

- Strix Issues: https://github.com/usestrix/strix/issues
- Railway Support: https://railway.app/help
- Claude API: https://support.anthropic.com

## Updates

### Update Strix Version

```dockerfile
# Dockerfile
RUN pip install --no-cache-dir strix-agent==1.8.0  # specify version
```

### Update Python Dependencies

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
git commit -am "Update dependencies"
git push
```

Railway will auto-deploy the update.
