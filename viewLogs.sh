#!/bin/bash

# View logs script for mcp-crawl4ai-rag server
cd "$(dirname "$0")"

# Check if server.log exists
if [ ! -f "server.log" ]; then
    echo "❌ No server.log file found"
    echo "💡 Start the server first with ./start-server.sh"
    exit 1
fi

echo "📝 Following mcp-crawl4ai-rag server logs..."
echo "🔄 Press Ctrl+C to stop viewing logs"
echo "----------------------------------------"

# Follow the log file
tail -f server.log
