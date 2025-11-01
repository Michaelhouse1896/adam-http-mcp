#!/bin/bash
# Simple script to test the ADAM MCP server

# Default to localhost, but allow custom URL
URL="${1:-http://10.211.55.3:8000/mcp}"

echo "Testing MCP server at: $URL"
echo "================================"
echo ""

# Step 1: Initialize session
echo "Step 1: Initializing MCP session..."
RESPONSE=$(curl -s -i -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}')

# Extract session ID
SESSION_ID=$(echo "$RESPONSE" | grep -i "Mcp-Session-Id:" | cut -d' ' -f2 | tr -d '\r\n')

if [ -z "$SESSION_ID" ]; then
    echo "ERROR: Failed to get session ID"
    echo "Response:"
    echo "$RESPONSE"
    exit 1
fi

echo "✓ Session ID obtained: $SESSION_ID"
echo ""

# Step 2: List available tools
echo "Step 2: Listing available MCP tools..."
TOOLS_RESPONSE=$(curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}')

echo "$TOOLS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TOOLS_RESPONSE"
echo ""

# Count tools
TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | grep -o '"name"' | wc -l)
echo "✓ Found $TOOL_COUNT MCP tools"
echo ""
echo "Test completed successfully!"
