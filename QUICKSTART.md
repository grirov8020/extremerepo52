# ⚡ Quick Start - Deploy in 3 Minutes

## 🚀 Fastest Deployment (Railway)

### Step 1: Get Claude API Key
1. Go to https://console.anthropic.com
2. Create account and get API key (starts with `sk-ant-api03-`)

### Step 2: Extract Files
```bash
tar -xzf strix-railway.tar.gz
cd strix-railway
```

### Step 3: Deploy
```bash
chmod +x deploy.sh
./deploy.sh
```

**That's it!** The script will:
- Install Railway CLI
- Create project
- Set API key
- Deploy app
- Open in browser

---

## 🐳 Local Testing (Docker)

```bash
# Extract
tar -xzf strix-railway.tar.gz
cd strix-railway

# Set API key
export ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Run
docker-compose up
```

Open http://localhost:8080

---

## 🐍 Local Testing (Python)

```bash
# Extract
tar -xzf strix-railway.tar.gz
cd strix-railway

# Install
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Run
python app.py
```

Open http://localhost:8080

---

## 🌐 GitHub + Railway Auto-Deploy

### 1. Create GitHub repo
```bash
cd strix-railway
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/strix-railway.git
git push -u origin main
```

### 2. Connect Railway
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `strix-railway` repository
5. Add environment variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: `sk-ant-api03-your-key-here`
6. Click "Deploy"

### 3. Done!
Every push to `main` branch auto-deploys 🎉

---

## 🎯 First Pentest

1. Open deployed app URL
2. Enter target: `https://example.com`
3. Select scan type: **Web Application**
4. Click "🚀 Launch Pentest"
5. Wait 5-15 minutes
6. View AI-powered security analysis

---

## 📋 What You Get

✅ Web interface for launching pentests  
✅ Claude Sonnet 4-6 AI security analysis  
✅ Real-time scan status  
✅ Downloadable markdown reports  
✅ OWASP Top 10 vulnerability detection  
✅ Automated exploit validation  

---

## 💰 Costs

- **Railway**: Free tier (500 hours/month)
- **Claude API**: ~$0.10 - $1.00 per full scan
- **Total**: Mostly free for testing

---

## 🆘 Troubleshooting

### "Railway CLI not found"
```bash
npm install -g @railway/cli
```

### "Docker not found"
Install Docker Desktop: https://www.docker.com/products/docker-desktop

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### "Permission denied: deploy.sh"
```bash
chmod +x deploy.sh
```

---

## 📚 More Documentation

- **Full Guide**: See `README.md`
- **Deployment**: See `DEPLOY.md`
- **Project Structure**: See `PROJECT_STRUCTURE.md`
- **Changelog**: See `CHANGELOG.md`

---

## 🔗 Quick Links

- Get API Key: https://console.anthropic.com
- Railway Dashboard: https://railway.app
- Strix GitHub: https://github.com/usestrix/strix
- Discord: https://discord.gg/strix-ai

---

**Need help?** Open an issue on GitHub or join Discord!

**Ready to hack?** Run `./deploy.sh` and start pentesting! 🦉
