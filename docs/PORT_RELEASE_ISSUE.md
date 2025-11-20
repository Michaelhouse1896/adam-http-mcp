# Port Release Issue - "Address Already in Use" Error

## Problem

When the ADAM MCP server is stopped (either via Ctrl+C or when Claude Desktop disconnects), the server process doesn't always release port 8000 immediately, causing "address already in use" errors on restart.

## Root Causes

1. **TCP TIME_WAIT State**: When a TCP socket is closed, it enters a TIME_WAIT state (typically 60 seconds on macOS) to ensure any delayed packets are properly handled. During this time, the port cannot be reused.

2. **Ungraceful Shutdown**: If the Python process is killed abruptly (SIGKILL), it doesn't have a chance to properly close sockets and clean up resources.

3. **Background Processes**: Sometimes the server process continues running in the background after Claude Desktop disconnects.

## Solutions Implemented

### 1. Signal Handlers (server.py:395-406)

Added proper signal handlers for graceful shutdown:

```python
def signal_handler(sig, frame):
    print("\n\nShutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill command
```

### 2. Management Script (manage_server.sh)

Created a helper script to manage the server lifecycle:

```bash
./manage_server.sh start    # Start the server
./manage_server.sh stop     # Gracefully stop (with force kill fallback)
./manage_server.sh restart  # Restart the server
./manage_server.sh status   # Check if server is running
```

### 3. Systemd Service Configuration (adam-mcp.service:14-17)

Updated systemd service with proper shutdown settings for production.

## Quick Fixes

### If Port is Stuck

**Option 1: Use the management script**
```bash
cd /path/to/adam-mcp
./manage_server.sh stop
```

**Option 2: Find and kill the process manually**
```bash
# Find the process using port 8000
lsof -i :8000 | grep LISTEN

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

**Option 3: Change the port temporarily**
```bash
# Edit .env file
MCP_PORT=8001
```

## Best Practices

1. **Development**: Use `./manage_server.sh` for all server operations
2. **Production**: Let systemd handle service lifecycle
3. **Testing**: Always check status before starting: `./manage_server.sh status`
4. **Cleanup**: Run `./manage_server.sh stop` before switching branches or updating code
