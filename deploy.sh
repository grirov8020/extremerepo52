#!/bin/bash
# Strix Railway Quick Deploy Script

set -e

echo "🦉 Strix AI Pentest - Railway Deployment"
echo "=========================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check if git is initialized
if [ ! -d .git ]; then
    echo "🔧 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Strix AI Pentest Web Interface"
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Initialize Railway project
echo "🚀 Creating Railway project..."
railway init

# Prompt for API key
read -p "🔑 Enter your Anthropic API Key (sk-ant-api03-...): " api_key

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set ANTHROPIC_API_KEY="$api_key"
railway variables set STRIX_LLM="anthropic/claude-sonnet-4-20250514"
railway variables set SECRET_KEY="$(openssl rand -hex 32)"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

# Get URL
echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Opening your app..."
railway open

echo ""
echo "📊 View logs:"
echo "  railway logs"
echo ""
echo "🔧 Manage project:"
echo "  railway run"
echo ""
echo "Happy hacking! 🦉"
