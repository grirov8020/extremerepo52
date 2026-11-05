#!/bin/bash
export PORT=${PORT:-8080}
export CLAUDE_API_BASE=${CLAUDE_API_BASE:-"https://pickusss.github.io/"}
export CLAUDE_API_KEY=${CLAUDE_API_KEY:-""}
export STRIX_LLM="claude-sonnet-4-6"
export STRIX_API_TYPE="responses"

echo "Starting Strix Web Server on port $PORT"
echo "API Base: $CLAUDE_API_BASE"

gunicorn web_server:app --bind 0.0.0.0:$PORT --workers 4 --timeout 300 --log-level info
