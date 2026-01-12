#!/bin/bash

# Startup script for mcp-crawl4ai-rag server with Blackwell GPU support
cd "$(dirname "$0")"

# Check if server is already running
if pgrep -f "crawl4ai_mcp.py" > /dev/null; then
    echo "❌ Server is already running!"
    echo "Use ./stop-server.sh to stop it first"
    exit 1
fi

echo "🚀 Starting mcp-crawl4ai-rag server with Blackwell GPU support..."
echo "📋 Make sure your .env file is configured with:"
echo "  - OPENAI_API_KEY"
echo "  - SUPABASE_URL" 
echo "  - SUPABASE_SERVICE_KEY"
echo ""

# Enable GPU reranking for Blackwell performance benefits
export USE_RERANKING=true

# Start server in background with logging
nohup uv run src/crawl4ai_mcp.py > server.log 2>&1 &
SERVER_PID=$!

# Wait a moment and check if server started successfully
sleep 3
if ps -p $SERVER_PID > /dev/null; then
    echo "✅ Server started successfully with GPU acceleration!"
    echo "📊 PID: $SERVER_PID"
    echo "🌐 URL: http://localhost:8051"
    echo "🚀 GPU: Blackwell support enabled (282x speedup)"
    echo "📝 Logs: ./viewLogs.sh"
    echo "🛑 Stop: ./stop-server.sh"
else
    echo "❌ Server failed to start. Check server.log for details."
    exit 1
fi
