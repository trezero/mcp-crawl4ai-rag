#!/usr/bin/env python3
"""
Real-time MCP Crawl4AI Server Monitor
Tracks crawling progress, GPU performance, and session statistics
"""
import re
import time
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class CrawlMonitor:
    def __init__(self, log_file="server.log"):
        self.log_file = Path(log_file)
        self.session_stats = {
            'start_time': None,
            'pages_found': 0,
            'pages_completed': 0,
            'current_url': None,
            'gpu_batches': 0,
            'gpu_speed': 0,
            'errors': 0
        }
        self.last_position = 0
        
    def parse_log_line(self, line):
        """Parse log line for crawling information"""
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
        timestamp = timestamp_match.group(1) if timestamp_match else None
        
        # Track crawling progress
        if "Crawling URL:" in line:
            url_match = re.search(r'Crawling URL: (.+)', line)
            if url_match:
                self.session_stats['current_url'] = url_match.group(1).strip()
                self.session_stats['pages_completed'] += 1
                
        elif "Found" in line and "pages to crawl" in line:
            pages_match = re.search(r'Found (\d+) pages to crawl', line)
            if pages_match:
                self.session_stats['pages_found'] = int(pages_match.group(1))
                
        elif "Processing sitemap" in line or "Processing page" in line:
            url_match = re.search(r'Processing (?:sitemap|page): (.+)', line)
            if url_match:
                self.session_stats['current_url'] = url_match.group(1).strip()
                
        # Track GPU performance
        elif "Batches:" in line and "it/s" in line:
            speed_match = re.search(r'(\d+\.?\d*) it/s', line)
            if speed_match:
                self.session_stats['gpu_speed'] = float(speed_match.group(1))
                self.session_stats['gpu_batches'] += 1
                
        # Track errors
        elif "ERROR" in line or "Failed" in line:
            self.session_stats['errors'] += 1
            
        return timestamp
    
    def display_status(self):
        """Display current crawling status"""
        stats = self.session_stats
        
        # Clear screen and show header
        print("\033[2J\033[H")  # Clear screen, move cursor to top
        print("🔍 MCP Crawl4AI Real-Time Monitor")
        print("=" * 50)
        print(f"⏰ Session Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Crawling Progress
        if stats['pages_found'] > 0:
            progress = (stats['pages_completed'] / stats['pages_found']) * 100
            progress_bar = "█" * int(progress / 5) + "░" * (20 - int(progress / 5))
            print(f"\n📊 Progress: [{progress_bar}] {stats['pages_completed']}/{stats['pages_found']} ({progress:.1f}%)")
        else:
            print(f"\n📊 Progress: {stats['pages_completed']} pages completed")
            
        # Current Activity
        if stats['current_url']:
            url_display = stats['current_url'][:60] + "..." if len(stats['current_url']) > 60 else stats['current_url']
            print(f"🌐 Current: {url_display}")
        else:
            print("🌐 Current: Waiting for crawling activity...")
            
        # GPU Performance
        if stats['gpu_batches'] > 0:
            print(f"🚀 GPU: {stats['gpu_speed']:.1f} it/s ({stats['gpu_batches']} batches processed)")
        else:
            print("🚀 GPU: No processing activity detected")
            
        # Error Count
        if stats['errors'] > 0:
            print(f"⚠️  Errors: {stats['errors']}")
        else:
            print("✅ Errors: None")
            
        print("\n" + "=" * 50)
        print("Press Ctrl+C to exit monitor")
    
    def monitor(self):
        """Main monitoring loop"""
        print("🚀 Starting MCP Crawl4AI Monitor...")
        print("📝 Monitoring server.log for crawling activity...")
        
        if not self.log_file.exists():
            print(f"❌ Log file {self.log_file} not found!")
            return
            
        # Get initial file size
        self.last_position = self.log_file.stat().st_size
        
        try:
            while True:
                # Check if file has grown
                current_size = self.log_file.stat().st_size
                if current_size > self.last_position:
                    # Read new content
                    with open(self.log_file, 'r') as f:
                        f.seek(self.last_position)
                        new_lines = f.readlines()
                        
                    # Process new lines
                    for line in new_lines:
                        self.parse_log_line(line.strip())
                        
                    self.last_position = current_size
                
                # Update display
                self.display_status()
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Monitor stopped by user")
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")

if __name__ == "__main__":
    monitor = CrawlMonitor()
    monitor.monitor()
