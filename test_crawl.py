#!/usr/bin/env python3
import asyncio
import time
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def test_single_page_crawl():
    """Test single page crawling performance with Blackwell GPU support"""
    url = "https://docs.datacore.com/SSV-WebHelp/SSV-WebHelp/Welcome_to_DataCore_SANsymphony_Help.htm"
    
    print(f"Testing single page crawl performance for Epic 11")
    print(f"Target URL: {url}")
    print(f"Starting crawl at: {datetime.now()}")
    
    start_time = time.time()
    
    try:
        # Configure browser for optimal performance
        browser_config = BrowserConfig(
            headless=True,
            verbose=False
        )
        
        # Configure crawl settings - simplified
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            stream=False,
            word_count_threshold=10
        )
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n=== CRAWL RESULTS ===")
            print(f"Success: {result.success}")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Status Code: {result.status_code}")
            
            if result.success:
                content_length = len(result.markdown) if result.markdown else 0
                html_length = len(result.html) if result.html else 0
                
                print(f"Content Length (markdown): {content_length:,} characters")
                print(f"Content Length (HTML): {html_length:,} characters")
                print(f"Processing Speed: {content_length/duration:.0f} chars/second")
                
                # Show first 200 chars of content
                if result.markdown:
                    print(f"\nFirst 200 characters:")
                    print(result.markdown[:200] + "...")
                    
                return {
                    "success": True,
                    "duration": duration,
                    "content_length": content_length,
                    "processing_speed": content_length/duration if duration > 0 else 0
                }
            else:
                print(f"Error: {result.error_message}")
                return {"success": False, "error": result.error_message}
                
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"Exception after {duration:.2f} seconds: {e}")
        return {"success": False, "error": str(e), "duration": duration}

if __name__ == "__main__":
    result = asyncio.run(test_single_page_crawl())
    print(f"\nFinal result: {result}")
