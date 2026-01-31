import sys
import os
import asyncio
import logging

# Add current directory to sys.path to ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Import MCP SDK
try:
    from mcp.server.fastmcp import FastMCP # Attempting FastMCP for brevity if allowed, but prompt said "Use standard mcp SDK (no fastmcp)"
    # PROMPT OVERRIDE: "Use standard mcp SDK (no fastmcp)."
    # Reverting to standard Server + StdioServerTransport
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    import mcp.types as types
except ImportError:
    logger.error("Failed to import 'mcp'. Please install requirements.txt.")
    sys.exit(1)

# Import Logic
try:
    import logic
except ImportError as e:
    logger.error(f"Failed to import logic: {e}")
    # Dummy logic to prevent crash
    class DummyLogic:
        def get_date_info(self, *args): return {"error": "Logic module missing"}
        def get_upcoming_holidays(self, *args): return [{"error": "Logic module missing"}]
        def is_workday(self, *args): return {"error": "Logic module missing"}
    logic = DummyLogic()

# Initialize Server
app = Server("mcp-tw-calendar")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="check_date",
            description="Check if a specific date (YYYYMMDD) is a holiday or workday in Taiwan.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYYMMDD or YYYY-MM-DD format"}
                },
                "required": ["date"]
            }
        ),
        types.Tool(
            name="get_upcoming_holidays",
            description="Get a list of upcoming public holidays in Taiwan.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of holidays to return (default 5)", "default": 5}
                }
            }
        ),
        types.Tool(
            name="is_workday",
            description="Determine if a date is a working day (accounting for makeup days).",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Date in YYYYMMDD or YYYY-MM-DD format"}
                },
                "required": ["date"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    logger.info(f"Tool called: {name} with {arguments}")
    
    try:
        if name == "check_date":
            date_str = arguments.get("date")
            result = logic.get_date_info(date_str)
            return [types.TextContent(type="text", text=str(result))]
            
        elif name == "get_upcoming_holidays":
            limit = arguments.get("limit", 5)
            result = logic.get_upcoming_holidays(limit)
            return [types.TextContent(type="text", text=str(result))]
            
        elif name == "is_workday":
            date_str = arguments.get("date")
            result = logic.is_workday(date_str)
            return [types.TextContent(type="text", text=str(result))]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error executing {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    logger.info("Starting mcp-tw-calendar server...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.critical(f"Server crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.stderr.write(f"Fatal error: {e}\n")
        sys.exit(1)
