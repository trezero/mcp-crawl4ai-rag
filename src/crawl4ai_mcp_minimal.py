#!/usr/bin/env python3
"""
Minimal MCP server for crawl4ai-rag that starts quickly
"""
import asyncio
import json
import sys
from mcp.server.fastmcp import FastMCP

# Create minimal MCP server
mcp = FastMCP("crawl4ai-rag")

@mcp.tool()
def test_connection() -> str:
    """Test if the MCP server is working"""
    return "✅ crawl4ai-rag MCP server is operational"

@mcp.tool()
def crawl_single_page(url: str) -> str:
    """Crawl a single web page (placeholder)"""
    return f"Would crawl: {url}"

@mcp.tool()
def perform_rag_query(query: str) -> str:
    """Perform RAG query (placeholder)"""
    return f"Would search for: {query}"

async def main():
    """Main entry point"""
    await mcp.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(main())
