#!/bin/bash

# Stop script for mcp-crawl4ai-rag server
cd "$(dirname "$0")"

echo "🛑 Stopping mcp-crawl4ai-rag server..."

# Find and kill crawl4ai processes
PIDS=$(pgrep -f "crawl4ai_mcp.py")

if [ -z "$PIDS" ]; then
    echo "❌ No server processes found running"
    exit 1
fi

echo "📋 Found server processes: $PIDS"

# Kill processes gracefully
for PID in $PIDS; do
    echo "🔄 Stopping process $PID..."
    kill $PID
done

# Wait for graceful shutdown
sleep 3

# Check if processes are still running and force kill if needed
REMAINING=$(pgrep -f "crawl4ai_mcp.py")
if [ ! -z "$REMAINING" ]; then
    echo "⚠️  Processes still running, force killing..."
    pkill -9 -f "crawl4ai_mcp.py"
    sleep 1
fi

# Final check
if pgrep -f "crawl4ai_mcp.py" > /dev/null; then
    echo "❌ Failed to stop server processes"
    exit 1
else
    echo "✅ Server stopped successfully!"
fi
