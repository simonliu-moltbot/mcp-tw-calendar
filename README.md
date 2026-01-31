# Taiwan Calendar MCP Server (mcp-tw-calendar)

A Model Context Protocol (MCP) server that provides Taiwan's official holiday and workday information.
Uses open data to handle complex logic like "Makeup Workdays" (補班日) and "Adjusted Holidays" (彈性放假).

## Features
- Check if a specific date is a holiday or workday.
- List upcoming holidays.
- Identify makeup workdays.

## Installation

1.  **Create venv**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

### Claude Desktop
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tw-calendar": {
      "command": "/absolute/path/to/projects/mcp-tw-calendar/.venv/bin/python",
      "args": ["/absolute/path/to/projects/mcp-tw-calendar/src/server.py"]
    }
  }
}
```

### Dive (Melt)
- **Type**: `stdio`
- **Command**: `[Path to Python]` (e.g. `/Users/username/projects/mcp-tw-calendar/.venv/bin/python`)
- **Args**: `[Path to Server]` (e.g. `/Users/username/projects/mcp-tw-calendar/src/server.py`)

## Data Source
Data is sourced from open community mirrors of the DGPA (Directorate-General of Personnel Administration) calendar.
