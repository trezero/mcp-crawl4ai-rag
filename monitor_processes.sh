#!/bin/bash

# Crawl4AI MCP Server Monitor and Cleanup Script
# This script monitors for orphaned Playwright processes and cleans them up

echo "🔍 MCP Crawl4AI Process Monitor"
echo "==============================="

while true; do
    # Count orphaned Playwright processes
    ORPHANED_COUNT=$(pgrep -f "playwright/driver/node.*run-driver" 2>/dev/null | wc -l)
    
    if [ "$ORPHANED_COUNT" -gt 10 ]; then
        echo "⚠️  WARNING: Found $ORPHANED_COUNT orphaned Playwright processes"
        echo "🧹 Cleaning up orphaned processes..."
        pkill -f "playwright/driver/node.*run-driver" || true
        echo "✅ Cleanup completed"
    elif [ "$ORPHANED_COUNT" -gt 0 ]; then
        echo "📊 Found $ORPHANED_COUNT Playwright processes (normal)"
    else
        echo "✅ No orphaned Playwright processes found"
    fi
    
    # Check if MCP server is running
    MCP_COUNT=$(pgrep -f "python.*crawl4ai_mcp.py" 2>/dev/null | wc -l)
    if [ "$MCP_COUNT" -eq 0 ]; then
        echo "⚠️  MCP server is not running"
    else
        echo "✅ MCP server is running ($MCP_COUNT process)"
    fi
    
    echo "---"
    sleep 30
done
