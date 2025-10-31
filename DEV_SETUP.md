# Development Setup Guide

This guide will help you set up the ADAM MCP Server for local development and testing.

## Prerequisites

- Python 3.10 or newer
- pip (Python package manager)
- Git (for cloning the repository)
- ADAM API token (get from your ADAM administrator)
- Access to your ADAM instance API

## Quick Start

### 1. Clone the Repository

```bash
# Clone the repository from GitHub
git clone https://github.com/dominic-gruijters/adam-mcp.git

# Navigate to the project directory
cd adam-mcp
```

Alternatively, if you prefer SSH:

```bash
git clone git@github.com:dominic-gruijters/adam-mcp.git
cd adam-mcp
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt when activated.

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

This will install:
- `fastmcp` - MCP server framework
- `httpx` - HTTP client for API calls
- `python-dotenv` - Environment variable management
- `uvicorn` - ASGI server

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

Set these variables in `.env`:

```bash
# Your ADAM API token (30 characters)
ADAM_API_TOKEN=abc123def456ghi789jkl012mno345

# Full URL to your ADAM API (including /api)
ADAM_BASE_URL=https://yourschool.adam.co.za/api

# SSL certificate verification (true/false)
# Set to false for development with self-signed certificates
ADAM_VERIFY_SSL=true

# Optional: Customize server settings
MCP_SERVER_NAME=ADAM School MIS
MCP_HOST=127.0.0.1
MCP_PORT=8000
```

**Important**: Make sure `.env` is in your `.gitignore` to prevent committing sensitive tokens.

#### Self-Signed SSL Certificates (Development)

If your ADAM development server uses a self-signed SSL certificate, you'll get SSL verification errors. To fix this:

1. **Option 1: Disable SSL verification** (development only):
   ```bash
   ADAM_VERIFY_SSL=false
   ```

2. **Option 2: Use HTTP** (if available):
   ```bash
   ADAM_BASE_URL=http://localhost/api
   ```

**Security Warning**:
- ⚠️ Only disable SSL verification in trusted development environments
- ⚠️ NEVER disable SSL verification in production
- ✅ Production should always use properly signed SSL certificates with `ADAM_VERIFY_SSL=true`

### 5. Run the Development Server

```bash
# Make sure virtual environment is activated
python server.py
```

You should see output like:
```
Starting ADAM School MIS v1.0.0
Server will listen on 127.0.0.1:8000
Connecting to ADAM API: https://yourschool.adam.co.za/api

Available endpoints:
  - Streamable HTTP: http://127.0.0.1:8000/mcp

Press Ctrl+C to stop the server
```

The server is now running locally on `http://127.0.0.1:8000/mcp`

**Important**: By default, the server listens on `127.0.0.1` (localhost only). This means:
- ✅ You can access it via `http://127.0.0.1:8000/mcp` or `http://localhost:8000/mcp`
- ❌ You cannot access it via `http://adam.local:8000/mcp` or from other machines
- This is the recommended setting for development (more secure)

**To allow access from other machines or domains** (e.g., `adam.local`, VMs):
1. Edit your `.env` file and change:
   ```bash
   MCP_HOST=0.0.0.0  # Listen on all network interfaces
   ```
2. Restart the server
3. Now you can access via hostname or IP address

**For VM development** (recommended):
- Use the VM's IP address directly instead of `.local` hostnames for better performance
- Example: `http://10.211.55.3:8000/mcp` instead of `http://adam.local:8000/mcp`
- This avoids mDNS/Bonjour resolution overhead

**Security Note**: Only use `0.0.0.0` in trusted development environments. For production, always use a reverse proxy (Apache2/Nginx) with the server bound to `127.0.0.1`.

**Production Performance Note**: The networking overhead you experience in VM development (Mac → VM) won't exist in production because:
- The MCP server and Apache2 run on the **same Ubuntu server**
- Apache2 proxies to `127.0.0.1:8000` (localhost, no network hop)
- Teachers connect via properly configured DNS (not mDNS/Bonjour)
- Result: Sub-100ms response times instead of multi-second VM network delays

## Testing the Server

### Test the Connection (Localhost)

1. Keep the server running in one terminal
2. In another terminal, test the endpoint:

```bash
# Basic connectivity test (will show "Not Acceptable" error - this is expected!)
curl http://127.0.0.1:8000/mcp

# Expected response:
# {"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept text/event-stream"}}
# This means the server is running correctly!
```

**To properly test MCP protocol**, you need to initialize a session first:

```bash
# Step 1: Initialize the MCP session
curl -v -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}'

# Look for the "Mcp-Session-Id" header in the response
# Example: Mcp-Session-Id: abc123def456...

# Step 2: Use the session ID for subsequent requests
SESSION_ID="<paste-session-id-here>"

curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# This should return a JSON-RPC response with the list of available tools
```

**Simplified testing script**:
```bash
# Save this as test_mcp.sh
#!/bin/bash
URL="http://127.0.0.1:8000/mcp"

# Initialize and extract session ID
RESPONSE=$(curl -i -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}')

SESSION_ID=$(echo "$RESPONSE" | grep -i "Mcp-Session-Id:" | cut -d' ' -f2 | tr -d '\r')

echo "Session ID: $SESSION_ID"

# List tools
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

If you configured `MCP_HOST=0.0.0.0`, you can also test via:
```bash
# Test via hostname (if DNS/hosts configured)
curl http://adam.local:8000/mcp

# Test via IP address
curl http://YOUR_IP_ADDRESS:8000/mcp
```

**Note**: Claude Desktop handles all the MCP protocol details automatically, so you don't need to worry about headers when using it!

### Test with Claude Desktop (Local Development)

1. **Configure Claude Desktop to use your local server**

   Edit your Claude Desktop config file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

   **For localhost testing** (recommended):
   ```json
   {
     "mcpServers": {
       "adam-dev": {
         "command": "npx",
         "args": ["-y", "mcp-remote", "http://127.0.0.1:8000/mcp"]
       }
     }
   }
   ```

   **For testing via VM** (use IP address for best performance):
   ```json
   {
     "mcpServers": {
       "adam-dev": {
         "command": "npx",
         "args": ["-y", "mcp-remote", "http://10.211.55.3:8000/mcp", "--allow-http"]
       }
     }
   }
   ```

   Replace `10.211.55.3` with your VM's IP address. Using IP addresses avoids mDNS/Bonjour lookup overhead compared to `.local` hostnames.

   **Notes**:
   - `mcp-remote` allows HTTP for `localhost`/`127.0.0.1` by default
   - For other hostnames (like `adam.local`), add `--allow-http` flag
   - For production, always use HTTPS (no flag needed)
   - Claude Desktop will automatically download `mcp-remote` on first use

2. **Restart Claude Desktop**

3. **Test the connection**

   In Claude Desktop, try:
   - "Search for pupils named Smith"
   - "Test the ADAM connection"
   - "Get information for pupil 12345"

4. **View Server Logs**

   Watch the terminal where `server.py` is running to see requests coming in.

## Development Workflow

### Keeping Your Repository Updated

Before starting work, make sure you have the latest changes:

```bash
# Pull latest changes from GitHub
git pull origin main

# Check current status
git status
```

### Making Code Changes

1. **Create a feature branch** (optional but recommended):
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Stop the server** (Ctrl+C)

3. **Make your changes** to `server.py`, `adam_api.py`, or `config.py`

4. **Restart the server** (`python server.py`)

5. **Test your changes** in Claude Desktop or with curl

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

7. **Push to GitHub** (if working on a branch):
   ```bash
   git push origin feature/my-new-feature
   ```

### Common Development Tasks

#### Add a New Tool

1. Add the API method to `adam_api.py`:
   ```python
   async def get_something_new(self, param: str) -> dict[str, Any]:
       """Your API method."""
       return await self._make_request("Module", "resource", [param])
   ```

2. Add the tool to `server.py`:
   ```python
   @mcp.tool()
   async def get_something_new(param: str) -> str:
       """Description of what this tool does."""
       try:
           result = await api_client.get_something_new(param)
           return f"Results:\n{_format_json(result)}"
       except AdamAPIError as e:
           return f"Error: {e.message}"
   ```

3. Restart the server and test

#### Update Configuration

Edit `.env` and restart the server for changes to take effect.

#### View Detailed Logs

Run with more verbose logging:
```bash
python server.py
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

1. Change the port in `.env`:
   ```bash
   MCP_PORT=8001
   ```

2. Update your Claude Desktop config to use the new port:
   ```json
   "url": "http://127.0.0.1:8001/mcp"
   ```

### Import Errors

If you get import errors:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### Configuration Errors

If you see "Configuration Error":
- Verify `.env` file exists
- Check ADAM_API_TOKEN is exactly 30 characters
- Ensure ADAM_BASE_URL includes the full URL with `/api`

### ADAM API Connection Errors

1. **Test your API token directly:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        https://yourschool.adam.co.za/api/APIRequests/test
   ```

2. **Check the token has proper permissions** in ADAM admin panel

3. **Verify the base URL** is correct (should end with `/api`)

### Claude Desktop Not Connecting

1. **Verify the server is running** (`curl http://127.0.0.1:8000/mcp`)
2. **Check Claude Desktop config** syntax is valid JSON
3. **Restart Claude Desktop** completely
4. **Look for the hammer icon** 🔨 in Claude Desktop (bottom-right)

## Development Tips

### Use Auto-Reload During Development

Install `watchfiles` for auto-reload on code changes:

```bash
pip install watchfiles

# Run with auto-reload
uvicorn server:mcp.get_asgi_app --reload --host 127.0.0.1 --port 8000
```

However, note that `server.py` uses a direct run method. For auto-reload, you may need to adjust.

### Testing API Endpoints

Create a simple test script `test_api.py`:

```python
import asyncio
from adam_api import AdamAPIClient

async def test():
    client = AdamAPIClient()

    # Test connection
    result = await client.test_connection()
    print(result)

    # Test pupil search
    search_result = await client.search_pupils("Smith")
    print(search_result)

if __name__ == "__main__":
    asyncio.run(test())
```

Run it:
```bash
python test_api.py
```

### Enable Debug Mode

Add debug logging to see more details:

```python
# Add to top of server.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

Once you've tested locally:

1. **Review DEPLOYMENT.md** for production deployment instructions
2. **Set up on your Ubuntu server** with Apache2
3. **Configure systemd** for automatic startup
4. **Share the production URL** with your staff

## Getting Help

- Check the ADAM API docs: https://help.adam.co.za/api-access-to-adam.html
- Review FastMCP docs: https://github.com/jlowin/fastmcp
- Test API endpoints directly with curl to isolate issues
- Check server logs for error messages

## Virtual Environment Management

### Deactivate Virtual Environment

When you're done developing:
```bash
deactivate
```

### Reactivate Later

Next time you want to work on the project:
```bash
cd ~/Documents/adam_mcp
source venv/bin/activate  # macOS/Linux
python server.py
```

### Update Dependencies

If `requirements.txt` changes:
```bash
pip install --upgrade -r requirements.txt
```

## Clean Installation

If you need to start fresh:

```bash
# Remove virtual environment
rm -rf venv

# Remove .env (be careful - this deletes your config!)
rm .env

# Start over from step 2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```
