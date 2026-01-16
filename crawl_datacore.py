#!/usr/bin/env python3
import asyncio
import json
import aiohttp
import sys

async def call_mcp_tool(tool_name, arguments):
    """Call an MCP tool via HTTP"""
    url = "http://localhost:8051"
    
    # MCP protocol message
    message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{url}/message", json=message) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    print(f"HTTP Error: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return None
    except Exception as e:
        print(f"Error calling MCP tool: {e}")
        return None

async def main():
    print("🚀 Starting DataCore documentation crawl...")
    
    # First check available sources
    print("\n📊 Checking current sources...")
    sources_result = await call_mcp_tool("get_available_sources", {})
    if sources_result:
        print(f"Current sources: {sources_result}")
    
    # Crawl DataCore documentation
    print("\n🌐 Crawling DataCore documentation...")
    crawl_args = {
        "url": "https://docs.datacore.com/SSV-WebHelp/",
        "max_depth": 5,
        "max_concurrent": 3,
        "chunk_size": 3000
    }
    
    crawl_result = await call_mcp_tool("smart_crawl_url", crawl_args)
    if crawl_result:
        print(f"Crawl result: {crawl_result}")
    
    # Verify with a test query
    print("\n🔍 Testing RAG query...")
    query_result = await call_mcp_tool("perform_rag_query", {
        "query": "DataCore SANsymphony storage management",
        "max_results": 3
    })
    if query_result:
        print(f"Query result: {query_result}")

if __name__ == "__main__":
    asyncio.run(main())
