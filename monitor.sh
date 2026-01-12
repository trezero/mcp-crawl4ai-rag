#!/bin/bash

# Simple shell-based monitor for MCP Crawl4AI Server
cd "$(dirname "$0")"

LOG_FILE="server.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file $LOG_FILE not found!"
    exit 1
fi

echo "🔍 MCP Crawl4AI Simple Monitor"
echo "============================="

# Check for orphaned Playwright processes on startup
ORPHANED_COUNT=$(pgrep -f "playwright/driver/node.*run-driver" 2>/dev/null | wc -l)
if [ "$ORPHANED_COUNT" -gt 10 ]; then
    echo "⚠️  WARNING: Found $ORPHANED_COUNT orphaned Playwright processes"
    echo "🧹 Cleaning up orphaned processes..."
    pkill -f "playwright/driver/node.*run-driver" || true
    echo "✅ Cleanup completed"
fi

echo "📝 Monitoring $LOG_FILE for crawling activity..."
echo "Press Ctrl+C to exit"
echo ""

# Follow the log file and parse for crawling info
tail -f "$LOG_FILE" | while read line; do
    # Extract timestamp
    timestamp=$(echo "$line" | grep -o '^[0-9-]* [0-9:]*')
    
    # Check for crawling activity
    if echo "$line" | grep -q "🚀 Starting smart crawl"; then
        url=$(echo "$line" | sed 's/.*🚀 Starting smart crawl for: //')
        echo "[$timestamp] 🚀 STARTED: $url"
        
    elif echo "$line" | grep -q "Found.*URLs in sitemap"; then
        count=$(echo "$line" | grep -o '[0-9]* URLs')
        echo "[$timestamp] 📊 DISCOVERED: $count in sitemap"
        
    elif echo "$line" | grep -q "Processing page.*of"; then
        progress=$(echo "$line" | grep -o '[0-9]*/[0-9]*')
        url=$(echo "$line" | sed 's/.*: //' | cut -c1-50)
        echo "[$timestamp] 📄 PROGRESS: $progress - $url..."
        
    elif echo "$line" | grep -q "Successfully crawled.*pages"; then
        count=$(echo "$line" | grep -o '[0-9]* pages')
        echo "[$timestamp] ✅ COMPLETED: $count crawled"
        
    elif echo "$line" | grep -q "Batches:.*it/s"; then
        speed=$(echo "$line" | grep -o '[0-9.]*it/s')
        echo "[$timestamp] 🚀 GPU: $speed processing"
        
    elif echo "$line" | grep -q "ERROR\|Failed"; then
        error=$(echo "$line" | cut -c1-80)
        echo "[$timestamp] ❌ ERROR: $error..."
    fi
done
