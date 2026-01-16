import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    try:
        async with sse_client("http://localhost:8051/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List available tools
                tools = await session.list_tools()
                print(f"Available tools ({len(tools.tools)}):")
                for tool in tools.tools:
                    print(f"  - {tool.name}")
                
                # Check available sources
                print("\nChecking available sources...")
                result = await session.call_tool("get_available_sources", {})
                print(f"Sources: {result.content}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
