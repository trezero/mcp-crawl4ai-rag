#!/bin/bash

# Crawl4AI MCP Server Startup Script
# This script ensures Playwright browsers are installed before starting the server

set -e

echo "🚀 Starting Crawl4AI MCP Server..."

# Check if we're in the right directory
if [ ! -f "src/crawl4ai_mcp.py" ]; then
    echo "❌ Error: Must be run from the mcp-crawl4ai-rag directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run 'uv venv' first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if Playwright browsers are installed
if [ ! -d "$HOME/.cache/ms-playwright/chromium-"* ] 2>/dev/null; then
    echo "📦 Installing Playwright browsers..."
    playwright install
else
    echo "✅ Playwright browsers already installed"
fi

# Check for orphaned Playwright processes and clean them up
ORPHANED_COUNT=$(pgrep -f "playwright/driver/node.*run-driver" | wc -l)
if [ "$ORPHANED_COUNT" -gt 0 ]; then
    echo "🧹 Cleaning up $ORPHANED_COUNT orphaned Playwright processes..."
    pkill -f "playwright/driver/node.*run-driver" || true
fi

# Start the server
echo "🌟 Starting MCP server..."
exec uv run src/crawl4ai_mcp.py
