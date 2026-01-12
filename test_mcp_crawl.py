#!/usr/bin/env python3
import asyncio
import time
import json
from datetime import datetime
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append('src')

# Set up environment
project_root = Path(__file__).resolve().parent
dotenv_path = project_root / '.env'

from dotenv import load_dotenv
load_dotenv(dotenv_path, override=True)

async def test_mcp_crawl():
    """Test MCP server crawl_single_page tool performance"""
    url = "https://docs.datacore.com/SSV-WebHelp/SSV-WebHelp/Welcome_to_DataCore_SANsymphony_Help.htm"
    
    print(f"Testing MCP crawl_single_page tool for Epic 11")
    print(f"Target URL: {url}")
    print(f"Starting at: {datetime.now()}")
    
    start_time = time.time()
    
    try:
        # Import the MCP server components
        from crawl4ai_mcp import crawl_single_page, Crawl4AIContext
        from crawl4ai import AsyncWebCrawler, BrowserConfig
        from utils import get_supabase_client
        
        # Set up context similar to the MCP server
        browser_config = BrowserConfig(headless=True, verbose=False)
        crawler = AsyncWebCrawler(config=browser_config)
        await crawler.__aenter__()
        
        supabase_client = get_supabase_client()
        
        # Create a mock context
        class MockContext:
            def __init__(self, crawler, supabase_client):
                self.request_context = MockRequestContext(crawler, supabase_client)
        
        class MockRequestContext:
            def __init__(self, crawler, supabase_client):
                self.lifespan_context = MockLifespanContext(crawler, supabase_client)
        
        class MockLifespanContext:
            def __init__(self, crawler, supabase_client):
                self.crawler = crawler
                self.supabase_client = supabase_client
                self.reranking_model = None
        
        ctx = MockContext(crawler, supabase_client)
        
        # Call the MCP function
        result = await crawl_single_page(ctx, url)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n=== MCP CRAWL RESULTS ===")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Result length: {len(result)} characters")
        print(f"First 300 characters of result:")
        print(result[:300] + "...")
        
        # Clean up
        await crawler.__aexit__(None, None, None)
        
        return {
            "success": True,
            "duration": duration,
            "result_length": len(result)
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"Exception after {duration:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e), "duration": duration}

if __name__ == "__main__":
    result = asyncio.run(test_mcp_crawl())
    print(f"\nFinal MCP result: {result}")
