# Strix AI Pentest Web Interface

🦉 Autonomous AI penetration testing web application powered by **Claude Sonnet 4-6** and **Strix**.

## Features

- 🎯 **Web-based pentest launcher** - Start security scans through browser interface
- 🤖 **AI-powered analysis** - Claude Sonnet 4-6 provides expert security insights
- 📊 **Real-time scan tracking** - Monitor active pentests with live status updates
- 📝 **Detailed reports** - Export comprehensive security reports with PoCs
- 🔒 **Multiple scan types** - Web apps, APIs, full pentests with OWASP coverage
- ⚡ **Fast deployment** - One-click deploy to Railway

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

### Manual Deployment Steps

1. **Clone this repository:**
   ```bash
   git clone <your-repo-url>
   cd strix-railway
   ```

2. **Create Railway project:**
   ```bash
   railway init
   ```

3. **Set environment variables in Railway dashboard:**
   ```env
   ANTHROPIC_API_KEY=your_claude_api_key_here
   PORT=8080
   SECRET_KEY=your_random_secret_key
   STRIX_LLM=anthropic/claude-sonnet-4-20250514
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Open your app:**
   ```bash
   railway open
   ```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for Claude Sonnet 4-6 |
| `PORT` | No | Port to run on (default: 8080) |
| `SECRET_KEY` | No | Flask secret key (auto-generated if not set) |
| `STRIX_LLM` | No | LLM model to use (default: claude-sonnet-4-20250514) |
| `DEBUG` | No | Enable debug mode (default: false) |

## Usage

### Starting a Pentest

1. Open the web interface
2. Enter target URL or local path
3. Select scan type:
   - **Web Application** - Standard web app security testing
   - **API Endpoints** - REST/GraphQL API security
   - **Full Pentest** - Comprehensive security assessment
4. Configure options:
   - **Scan Depth** - How deep to scan (1-10)
   - **Aggressive Mode** - More thorough but noisier scans
   - **Stealth Mode** - Quieter scans to avoid detection
5. Click "Launch Pentest"

### Viewing Results

- Active scans appear in real-time in the "Active Scans" section
- When complete, click "View Results" to see:
  - **Claude AI Analysis** - Expert security insights and recommendations
  - **Raw Strix Output** - Detailed technical findings
  - **Downloadable Report** - Markdown format for documentation

## API Endpoints

### Start Scan
```http
POST /api/scan/start
Content-Type: application/json

{
  "target": "https://example.com",
  "scan_type": "web",
  "depth": 3,
  "aggressive": false,
  "stealth": false
}
```

Response:
```json
{
  "scan_id": "scan_20250101_120000_abc123",
  "message": "Scan started successfully"
}
```

### Get Scan Status
```http
GET /api/scan/{scan_id}/status
```

### Get Scan Results
```http
GET /api/scan/{scan_id}/results
```

### Download Report
```http
GET /api/scan/{scan_id}/download
```

### List All Scans
```http
GET /api/scans
```

### Health Check
```http
GET /health
```

## Local Development

### Prerequisites
- Python 3.12+
- Docker (for Strix sandbox)
- Anthropic API key

### Setup
```bash
# Clone repository
git clone <your-repo-url>
cd strix-railway

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=your_key_here
export STRIX_LLM=anthropic/claude-sonnet-4-20250514

# Run application
python app.py
```

Visit http://localhost:8080

## Architecture

```
┌─────────────────┐
│  Web Browser    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Flask Server   │◄─── templates/index.html
│    (app.py)     │
└────────┬────────┘
         │
         ├─────────────────────┐
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│  Strix CLI      │   │  Claude API     │
│  (subprocess)   │   │  (Anthropic)    │
└─────────────────┘   └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Docker         │
│  Sandbox        │
└─────────────────┘
```

## Security Notes

- **DO NOT** expose this publicly without authentication
- Use strong `SECRET_KEY` in production
- Restrict target scanning to authorized assets only
- Review Claude API usage limits and costs
- Consider VPN/firewall restrictions for pentest traffic

## Troubleshooting

### Docker not available
Ensure Docker is installed and running:
```bash
docker ps
```

### Claude API errors
Verify your API key:
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":1024,"messages":[{"role":"user","content":"test"}]}'
```

### Scan timeouts
Increase timeout in `app.py`:
```python
process.communicate(timeout=7200)  # 2 hours
```

## Credits

- **Strix** - https://github.com/usestrix/strix
- **Claude AI** - https://anthropic.com
- **Railway** - https://railway.app

## License

Apache 2.0 - See original Strix repository for full license
