# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP (Model Context Protocol) server that wraps the ADAM School Management Information System REST API, exposing it as tools for Claude Desktop. Teachers query pupil info, academic records, attendance, and contacts through natural language.

**Stack**: Python 3.10+ / FastMCP / httpx / uvicorn

## Development Commands

```bash
# Setup (requires Python >= 3.10; macOS Homebrew: /opt/homebrew/opt/python@3.13/bin/python3)
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cp .env.example .env   # then edit with real credentials

# Run in HTTP mode (dev/testing)
./manage_server.sh start          # recommended (handles port conflicts)
./manage_server.sh stop|restart|status
python server.py                  # alternative direct run → http://127.0.0.1:8000/mcp

# Run in stdio mode (Claude Desktop)
MCP_TRANSPORT=stdio python server.py    # or enable Project MCP Servers in Claude Desktop

# Test MCP protocol handshake (HTTP mode)
./test_mcp.sh                           # defaults to http://10.211.55.3:8000/mcp
./test_mcp.sh http://localhost:8000/mcp

# Test stdio mode
./test_stdio.sh

# Test ADAM API directly
curl -H "Authorization: Bearer YOUR_TOKEN" https://yourschool.adam.co.za/api/request/test

# Production (Ubuntu systemd + Apache2 reverse proxy)
sudo systemctl start|stop|restart|status adam-mcp
sudo journalctl -u adam-mcp -f
```

## Architecture

Three files, one responsibility each:

- **`server.py`** — MCP tool definitions (`@mcp.tool()` decorators). Each tool calls `AdamAPIClient`, catches `AdamAPIError`, returns formatted strings. Entry point supports both `stdio` and `http` transport via `MCP_TRANSPORT` env var.

- **`adam_api.py`** — `AdamAPIClient` wraps all ADAM HTTP requests. Central method `_make_request(module, resource, params)` builds path-segment URLs (NOT query params): `/api/{module}/{resource}/{param1}/{param2}`. Parameters are percent-encoded via `_encode_param()`. Name-based lookups (`find_pupils_by_name`, `find_families_by_name`, `find_staff_by_name`) fetch full datasets via Data Query API secrets and filter client-side.

- **`config.py`** — Loads `.env` at import time, validates on module load. Token must be exactly 30 chars. Warns (doesn't fail) if optional Data Query secrets are missing.

### ADAM API URL Pattern

```
/api/pupils/pupil/12345              (NOT ?id=12345)
/api/absentees/summarycount/2024-01-01/2024-01-31   (NOT ?from=...&to=...)
```

All parameters are path segments joined by `/`, percent-encoded.

### Data Flow for Name-Based Lookups

`find_pupil_by_name` → `get_all_pupils_data()` (Data Query API with secret) → client-side filter. Same pattern for families and staff. These require `ADAM_DATAQUERY_*_SECRET` env vars.

### Data Flow for Class Parent Emails

`get_class_parent_emails` orchestrates multiple API calls: grade registrations → filter by class description → per-pupil family relationships → per-family emails → deduplicate.

## Adding a New MCP Tool

1. Add async method to `AdamAPIClient` in `adam_api.py`:
   ```python
   async def get_something(self, param: str) -> dict[str, Any]:
       return await self._make_request("ModuleName", "resource", [param])
   ```

2. Add `@mcp.tool()` in `server.py`:
   ```python
   @mcp.tool()
   async def get_something(param: str) -> str:
       """User-facing description (shown in Claude Desktop)."""
       try:
           result = await api_client.get_something(param)
           return f"Results:\n{_format_json(result)}"
       except AdamAPIError as e:
           return f"Error: {e.message}"
   ```

3. Reference `API_DOCUMENTATION.md` for endpoint details. Dates must be `YYYY-MM-DD`.

## Configuration

All via `.env` (never committed). Required: `ADAM_API_TOKEN` (30 chars), `ADAM_BASE_URL` (full URL ending in `/api`). Optional: `ADAM_DATAQUERY_PUPILS_SECRET`, `ADAM_DATAQUERY_FAMILIES_SECRET`, `ADAM_DATAQUERY_STAFF_SECRET` (enable name lookups), `ADAM_VERIFY_SSL` (default `true`), `MCP_HOST` (default `127.0.0.1`), `MCP_PORT` (default `8000`).

## Deployment

- **Dev**: `python server.py` on localhost:8000. Set `MCP_HOST=0.0.0.0` for network access.
- **Production**: systemd service (`adam-mcp.service`) → `127.0.0.1:8000` → Apache2 reverse proxy (`apache2-adam-mcp.conf`) handles SSL at `https://school.adam.co.za/adam-mcp`.

## Known Issues

- The `describe_table` tool for ADAM MySQL MCP database does not work. Use MySQL `information_schema` queries instead.
- VM development (Mac → Parallels → Ubuntu) has multi-second response times due to mDNS overhead. Use IP addresses instead of `.local` hostnames.
