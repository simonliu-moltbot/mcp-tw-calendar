"""
Taiwan Calendar MCP Server using FastMCP.
Supports both STDIO and Streamable HTTP transport modes.
"""
import sys
import os
import argparse
import asyncio

# Add current directory to path so we can import 'logic'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
import logic

# Initialize FastMCP
mcp = FastMCP("mcp-tw-calendar")

@mcp.tool()
async def get_taiwan_holidays(year: int = 2026) -> str:
    """
    獲取台灣國定假日與補班補課資訊。
    Args:
        year: 西元年份 (預設 2026)。
    """
    data = await logic.fetch_calendar_data(year)
    return str(data)

def main():
    parser = argparse.ArgumentParser(description="Taiwan Calendar MCP Server")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio", help="Transport mode")
    parser.add_argument("--port", type=int, default=8000, help="HTTP port (only for http mode)")
    args = parser.parse_args()

    if args.mode == "stdio":
        mcp.run()
    else:
        print(f"Starting FastMCP in streamable-http mode on port {args.port}...", file=sys.stderr)
        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=args.port,
            path="/mcp"
        )

if __name__ == "__main__":
    main()
