#!/usr/bin/env python3
import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    try:
        # Import the MCP components
        from crawl4ai_mcp import crawl4ai_lifespan, smart_crawl_url, get_available_sources, perform_rag_query
        
        print("🚀 Starting DataCore documentation recovery...")
        
        # Initialize the crawler context
        async with crawl4ai_lifespan(None) as ctx_data:
            # Create a simple context wrapper
            class SimpleContext:
                def __init__(self, data):
                    self.data = data
            
            ctx = SimpleContext(ctx_data)
            
            # Check current sources
            print("\n📊 Checking current sources...")
            try:
                sources = await get_available_sources(ctx)
                print(f"Current sources: {sources}")
            except Exception as e:
                print(f"Error getting sources: {e}")
            
            # Crawl DataCore documentation
            print("\n🌐 Crawling DataCore documentation...")
            try:
                result = await smart_crawl_url(
                    ctx, 
                    "https://docs.datacore.com/SSV-WebHelp/",
                    max_depth=5,
                    max_concurrent=3,
                    chunk_size=3000
                )
                print(f"✅ Crawl completed: {result}")
            except Exception as e:
                print(f"❌ Crawl failed: {e}")
                return
            
            # Verify with test query
            print("\n🔍 Testing RAG query...")
            try:
                query_result = await perform_rag_query(
                    ctx,
                    "DataCore SANsymphony storage management",
                    max_results=3
                )
                print(f"✅ Query successful: {query_result}")
            except Exception as e:
                print(f"❌ Query failed: {e}")
            
            print("\n✅ DataCore documentation recovery completed!")
            
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
