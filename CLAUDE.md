# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that provides Claude Desktop with access to the ADAM School Management Information System API. It allows teachers and staff to query pupil information, academic records, attendance, and contact details through natural language in Claude Desktop.

**Architecture**: Python FastMCP server that wraps the ADAM REST API and exposes it as MCP tools.

## Development Commands

### Prerequisites

**Python 3.10 or higher is required.** The `fastmcp` dependency requires Python >=3.10.

- Check your Python version: `python3 --version`
- If using macOS with Homebrew Python 3.13: `/opt/homebrew/opt/python@3.13/bin/python3`
- If system Python is 3.9 or lower, use a newer Python installation to create the venv

### Setup and Running

```bash
# Create and activate virtual environment
# On macOS with Homebrew Python 3.13 (if system python3 is too old):
/opt/homebrew/opt/python@3.13/bin/python3 -m venv venv

# Or with system python3 if it's >= 3.10:
python3 -m venv venv

source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment (copy and edit .env)
cp .env.example .env
# Edit .env with your ADAM_API_TOKEN and ADAM_BASE_URL
```

### Running the Server

**For Claude Desktop (stdio mode - no manual venv activation needed):**

The project includes `mcpServers.json` which configures the server to run in stdio mode.
Claude Desktop (or other MCP clients) will automatically use the venv Python when launching the server.

```bash
# Enable in Claude Desktop settings:
# Settings → Developer → Enable Project MCP Servers
```

**For HTTP mode (development/testing):**

```bash
# Activate venv first
source venv/bin/activate

# Run development server (recommended - handles port conflicts gracefully)
./manage_server.sh start

# Alternative: Direct Python execution
python server.py

# Server will start on http://127.0.0.1:8000/mcp
```

### Server Management

Use the included management script for reliable server control:

```bash
./manage_server.sh start    # Start the server
./manage_server.sh stop     # Gracefully stop (handles stuck ports)
./manage_server.sh restart  # Restart the server
./manage_server.sh status   # Check if server is running
```

**Note**: If you encounter "address already in use" errors, run `./manage_server.sh stop` to properly clean up stuck processes.

### Testing

```bash
# Test MCP server connection
./test_mcp.sh

# Test with custom URL
./test_mcp.sh http://localhost:8000/mcp

# Test specific API endpoint directly
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://yourschool.adam.co.za/api/request/test
```

### Production Deployment

```bash
# Production runs as systemd service on Ubuntu
sudo systemctl start adam-mcp
sudo systemctl status adam-mcp
sudo journalctl -u adam-mcp -f  # View logs

# Restart after code changes
sudo systemctl restart adam-mcp
```

## Code Architecture

### Core Components

1. **server.py** - Main MCP server
   - Defines MCP tools using `@mcp.tool()` decorator
   - Each tool maps to a user-facing capability in Claude Desktop
   - Tools call methods from `AdamAPIClient`
   - Returns formatted strings for Claude to present to users

2. **adam_api.py** - ADAM API client wrapper
   - `AdamAPIClient` class handles all HTTP requests to ADAM API
   - `_make_request()` builds URLs in ADAM's format: `/api/{module}/{resource}/{param1}/{param2}`
   - Parameters are percent-encoded via `_encode_param()`
   - Error handling via custom `AdamAPIError` exception

3. **config.py** - Configuration management
   - Loads settings from `.env` file
   - Validates API token (must be 30 characters)
   - Manages SSL verification setting
   - Provides auth header: `Bearer {token}`

### ADAM API URL Format

The ADAM API uses path parameters (NOT query parameters):
```
Correct:   /api/pupils/pupil/12345
Incorrect: /api/pupils/pupil?id=12345

Correct:   /api/absentees/summarycount/2024-01-01/2024-01-31
Incorrect: /api/absentees/summarycount?from=2024-01-01&to=2024-01-31
```

This is why `_make_request()` builds URLs by joining path segments.

### SSL Certificate Handling

The codebase supports self-signed certificates for development:
- `ADAM_VERIFY_SSL=false` disables SSL verification (development only)
- `ADAM_VERIFY_SSL=true` enables verification (production default)
- Uses httpx's `verify` parameter in `AsyncClient`

**Important**: Never disable SSL verification in production.

### MCP Tools Pattern

When adding a new tool:

1. Add API method to `adam_api.py`:
```python
async def get_something(self, param: str) -> dict[str, Any]:
    """Get something from ADAM."""
    return await self._make_request("ModuleName", "resource", [param])
```

2. Add MCP tool to `server.py`:
```python
@mcp.tool()
async def get_something(param: str) -> str:
    """User-facing description of what this does."""
    try:
        result = await api_client.get_something(param)
        return f"Results:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error: {e.message}"
```

3. Tool should:
   - Have clear docstring (shown to users in Claude Desktop)
   - Return formatted string (not dict)
   - Handle errors gracefully with user-friendly messages

### Important API Endpoints Used

Reference `API_DOCUMENTATION.md` for complete endpoint details:

- `GET /api/pupils/pupil/{id}` - Pupil information
- `GET /api/classes/pupilteachers/{id}` - Teachers and classes
- `GET /api/reporting/subjectmarksbypupil/{id}` - Academic records
- `GET /api/families/email/{id}` - Family emails
- `GET /api/families/contactlist` - All family contacts
- `GET /api/absentees/summarycount/{from}/{to}` - Absence summary
- `GET /api/absentees/list/{from}/{to}` - Detailed absences
- `GET /api/request/test` - Connection test

### Deployment Architecture

**Development**:
- Runs directly via `python server.py`
- Listens on `127.0.0.1:8000` (localhost only)
- Can set `MCP_HOST=0.0.0.0` to allow network access

**Production**:
- Runs as systemd service (`adam-mcp.service`)
- Listens on `127.0.0.1:8000` (not exposed externally)
- Apache2 reverse proxy at `/adam-mcp` endpoint
- Apache handles SSL termination
- Teachers connect via: `https://school.adam.co.za/adam-mcp`

The systemd service ensures automatic startup and restart on failure.

### Configuration Files

- `.env` - Runtime configuration (NEVER commit this)
  - `ADAM_API_TOKEN` - 30-character API token
  - `ADAM_BASE_URL` - Full URL to ADAM API with `/api` path
  - `ADAM_VERIFY_SSL` - SSL verification (true/false)
  - `MCP_HOST` - Bind address (127.0.0.1 or 0.0.0.0)
  - `MCP_PORT` - Port number (default 8000)

- `.env.example` - Template with placeholder values

- `requirements.txt` - Python dependencies
  - `fastmcp` - MCP server framework
  - `httpx` - Async HTTP client
  - `python-dotenv` - Environment variable loading
  - `uvicorn` - ASGI server (used by FastMCP)

- `adam-mcp.service` - systemd service definition

- `apache2-adam-mcp.conf` - Apache virtual host configuration

### Testing the MCP Server

The `test_mcp.sh` script demonstrates the MCP protocol handshake:

1. Initialize session with `initialize` method
2. Extract `Mcp-Session-Id` header from response
3. Use session ID for subsequent requests
4. Call `tools/list` to verify tools are available

This is the same flow Claude Desktop uses automatically.

### Error Handling Strategy

- API errors return `AdamAPIError` with message and optional status code
- MCP tools catch errors and return user-friendly error messages as strings
- Configuration errors (missing .env, invalid token) fail at startup
- HTTP errors (network, timeout) are wrapped in `AdamAPIError`

### Important Constraints

1. **Parameter Encoding**: All URL parameters must be percent-encoded (spaces become `%20`, etc.)

2. **Token Format**: ADAM API tokens are exactly 30 characters. Config validation enforces this.

3. **SSL in Production**: Production MUST use valid SSL certificates and `ADAM_VERIFY_SSL=true`

4. **describe_table Issue**: As noted in global CLAUDE.md, the `describe_table` tool for adam mysql MCP database does not work. Use MySQL information schema for table information instead.

5. **Date Format**: ADAM API expects dates as `YYYY-MM-DD` (e.g., "2024-01-15")

### Common Development Tasks

**Adding a new MCP tool**:
1. Check `API_DOCUMENTATION.md` for the ADAM endpoint details
2. Add method to `AdamAPIClient` in `adam_api.py`
3. Add `@mcp.tool()` function in `server.py`
4. Test with `python server.py` and Claude Desktop

**Updating to latest code**:
```bash
git pull origin main
pip install -r requirements.txt  # If requirements changed
sudo systemctl restart adam-mcp  # Production
```

**Debugging API issues**:
- Check server logs: `sudo journalctl -u adam-mcp -f`
- Test endpoint directly with curl
- Verify token permissions in ADAM admin panel
- Check `ADAM_BASE_URL` includes full path with `/api`

### Network Performance Notes

Development on VM (Mac → Parallels → Ubuntu):
- May experience multi-second response times due to mDNS/network overhead
- Use IP addresses instead of `.local` hostnames for better performance
- Example: `http://10.211.55.3:8000/mcp` vs `http://adam.local:8000/mcp`

Production (Ubuntu server):
- MCP server and Apache2 on same machine
- Apache proxies to `127.0.0.1:8000` (localhost, no network hop)
- Sub-100ms response times expected
- Teachers connect via proper DNS (not mDNS)
