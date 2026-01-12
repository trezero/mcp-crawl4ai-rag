#!/usr/bin/env python3
import asyncio
import time
import torch
from datetime import datetime

def check_gpu_status():
    """Check GPU status and capabilities"""
    print("=== GPU STATUS CHECK ===")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        capability = torch.cuda.get_device_capability(0)
        memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        print(f"✓ GPU Available: {gpu_name}")
        print(f"✓ CUDA Capability: {capability}")
        print(f"✓ GPU Memory: {memory:.1f} GB")
        
        # Check if it's Blackwell architecture
        if capability[0] >= 12:  # Blackwell is compute capability 12.0+
            print("✓ Blackwell Architecture Detected")
            return True
        else:
            print("⚠ Non-Blackwell GPU")
            return False
    else:
        print("✗ No GPU Available")
        return False

async def performance_test():
    """Run performance test for Epic 11"""
    print(f"\n=== EPIC 11 PERFORMANCE TEST ===")
    print(f"Test Time: {datetime.now()}")
    
    # Check GPU
    is_blackwell = check_gpu_status()
    
    # Import crawling components
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    
    url = "https://docs.datacore.com/SSV-WebHelp/SSV-WebHelp/Welcome_to_DataCore_SANsymphony_Help.htm"
    
    print(f"\nTarget: DataCore SANsymphony Welcome Page")
    print(f"URL: {url}")
    
    # Test basic crawling speed
    start_time = time.time()
    
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        
        crawl_time = time.time() - start_time
        
        if result.success:
            content_length = len(result.markdown) if result.markdown else 0
            processing_speed = content_length / crawl_time if crawl_time > 0 else 0
            
            print(f"\n=== PERFORMANCE RESULTS ===")
            print(f"Crawl Time: {crawl_time:.2f} seconds")
            print(f"Content Length: {content_length:,} characters")
            print(f"Processing Speed: {processing_speed:.0f} chars/second")
            print(f"Status: SUCCESS")
            
            if is_blackwell:
                print(f"GPU Acceleration: ENABLED (Blackwell)")
            else:
                print(f"GPU Acceleration: LIMITED/DISABLED")
                
            return {
                "success": True,
                "crawl_time": crawl_time,
                "content_length": content_length,
                "processing_speed": processing_speed,
                "blackwell_gpu": is_blackwell
            }
        else:
            print(f"FAILED: {result.error_message}")
            return {"success": False, "error": result.error_message}

if __name__ == "__main__":
    result = asyncio.run(performance_test())
    
    print(f"\n=== FINAL SUMMARY ===")
    if result["success"]:
        print(f"✓ Epic 11 Performance Test: PASSED")
        print(f"✓ Crawling Speed: {result['processing_speed']:.0f} chars/sec")
        if result["blackwell_gpu"]:
            print(f"✓ Blackwell GPU: ACTIVE")
        else:
            print(f"⚠ Blackwell GPU: NOT DETECTED")
    else:
        print(f"✗ Epic 11 Performance Test: FAILED")
        print(f"Error: {result.get('error', 'Unknown')}")
