# Strix AI Pentest - Railway Deployment

AI-powered penetration testing framework with Claude Sonnet 4.6 integration and web interface.

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

## ⚙️ Environment Variables

Set these in Railway dashboard:

```bash
CLAUDE_API_BASE=https://pickusss.github.io/
CLAUDE_API_KEY=your-api-key-here
PORT=8080
```

## 📦 What's Included

- ✅ Web-based pentest interface
- ✅ Claude Sonnet 4.6 AI model integration
- ✅ Custom API base URL support
- ✅ Real-time scan monitoring
- ✅ Multiple target types (web apps, APIs, repositories)
- ✅ Automated vulnerability detection

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export CLAUDE_API_BASE="https://pickusss.github.io/"
export CLAUDE_API_KEY="your-key"

# Run server
python web_server.py
```

Access at: http://localhost:8080

## 🎯 Usage

1. Open web interface
2. Configure API settings (Base URL + API Key)
3. Test API connection
4. Enter target URL/repository
5. Launch pentest scan
6. Monitor results in real-time

## 🛠️ API Endpoints

- `GET /` - Web interface
- `POST /api/config` - Configure API settings
- `POST /api/scan` - Start new scan
- `GET /api/scan/<scan_id>` - Get scan status
- `GET /api/scans` - List all scans
- `POST /api/test` - Test API connection
- `GET /health` - Health check

## 🔒 Security Features

- AI-powered vulnerability detection
- OWASP Top 10 coverage
- API security testing
- Code repository analysis
- Automated exploit verification

## 📝 License

Based on Strix (Apache 2.0)

## ⚠️ Disclaimer

For authorized security testing only. Do not use on systems you don't own or have permission to test.
