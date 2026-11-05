## 🚀 Railway Deployment Guide

### Quick Deploy

1. **Fork/Upload to GitHub**
   - Create a new repository on GitHub
   - Upload all files from this archive
   - Commit and push

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Environment Variables**
   
   In Railway dashboard, add these variables:
   
   ```
   CLAUDE_API_BASE=https://pickusss.github.io/
   CLAUDE_API_KEY=your-actual-api-key
   PORT=8080
   ```

4. **Deploy & Access**
   - Railway will auto-deploy
   - Get your URL: `https://your-app.railway.app`
   - Open in browser and start pentesting!

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CLAUDE_API_BASE="https://pickusss.github.io/"
export CLAUDE_API_KEY="your-key"

# Run locally
python web_server.py

# Access at http://localhost:8080
```

### Usage Instructions

1. **Configure API** (first time only)
   - Enter your API Base URL: `https://pickusss.github.io/`
   - Enter your Claude API Key
   - Click "Test API Connection" to verify

2. **Start a Pentest Scan**
   - Enter target URL (e.g., `https://example.com`)
   - Select scan type:
     - Web Application - for websites
     - API Testing - for REST APIs
     - Code Repository - for GitHub repos
   - Click "Launch Pentest"

3. **Monitor Results**
   - Scans appear in "Active Scans" section
   - Auto-refreshes every 10 seconds
   - Click "View Details" to see findings

### API Endpoints

- `GET /` - Web UI
- `POST /api/config` - Configure Claude API
- `POST /api/scan` - Start new scan
- `GET /api/scan/<id>` - Get scan status
- `GET /api/scans` - List all scans
- `POST /api/test` - Test API connection
- `GET /health` - Health check

### Troubleshooting

**"Unknown model" error:**
- Make sure your API base URL is correct
- Verify your API key is valid
- Test connection first before starting scans

**Scans stuck in "running":**
- This is a demo - scans complete after 10 seconds
- For real scans, integrate full Strix agent logic

**Railway deployment fails:**
- Check that all files are uploaded
- Verify requirements.txt is correct
- Check Railway logs for errors

### Security Notes

⚠️ **Important:**
- Only test systems you own or have permission to test
- Keep your API key secure (use environment variables)
- Don't commit `.env` file to git

### Support

For issues with:
- **Strix**: https://github.com/usestrix/strix
- **Railway**: https://railway.app/help
- **Claude API**: Check your API provider docs

---

Made with 🔒 by modifying Strix for Railway deployment
