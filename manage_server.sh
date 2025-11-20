#!/bin/bash
# ADAM MCP Server Management Script

PORT="${MCP_PORT:-8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_port() {
    lsof -i :$PORT -t 2>/dev/null
}

start_server() {
    echo -e "${GREEN}Starting ADAM MCP Server...${NC}"

    # Check if port is already in use
    PID=$(check_port)
    if [ ! -z "$PID" ]; then
        echo -e "${YELLOW}Warning: Port $PORT is already in use by process $PID${NC}"
        echo "Run '$0 stop' first or '$0 restart' to force restart"
        return 1
    fi

    # Activate virtual environment and start server
    if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
        source "$SCRIPT_DIR/venv/bin/activate"
        cd "$SCRIPT_DIR"
        python server.py
    else
        echo -e "${RED}Error: Virtual environment not found${NC}"
        echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        return 1
    fi
}

stop_server() {
    echo -e "${YELLOW}Stopping ADAM MCP Server...${NC}"

    PID=$(check_port)
    if [ -z "$PID" ]; then
        echo -e "${GREEN}Server is not running${NC}"
        return 0
    fi

    echo "Found process $PID on port $PORT"
    echo "Sending SIGTERM (graceful shutdown)..."
    kill $PID 2>/dev/null

    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
        sleep 1
        if [ -z "$(check_port)" ]; then
            echo -e "${GREEN}✓ Server stopped gracefully${NC}"
            return 0
        fi
        echo "Waiting for shutdown... ($i/5)"
    done

    # Force kill if still running
    PID=$(check_port)
    if [ ! -z "$PID" ]; then
        echo -e "${RED}Force killing process $PID...${NC}"
        kill -9 $PID 2>/dev/null
        sleep 1
    fi

    if [ -z "$(check_port)" ]; then
        echo -e "${GREEN}✓ Server stopped${NC}"
    else
        echo -e "${RED}✗ Failed to stop server${NC}"
        return 1
    fi
}

status_server() {
    PID=$(check_port)
    if [ -z "$PID" ]; then
        echo -e "${YELLOW}Server is not running${NC}"
        return 1
    else
        echo -e "${GREEN}Server is running (PID: $PID)${NC}"
        echo "Listening on port: $PORT"
        lsof -i :$PORT
        return 0
    fi
}

restart_server() {
    echo -e "${YELLOW}Restarting ADAM MCP Server...${NC}"
    stop_server
    sleep 2
    start_server
}

case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        status_server
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the MCP server"
        echo "  stop    - Stop the MCP server (gracefully, then force if needed)"
        echo "  restart - Restart the MCP server"
        echo "  status  - Check if server is running"
        exit 1
        ;;
esac

exit $?
