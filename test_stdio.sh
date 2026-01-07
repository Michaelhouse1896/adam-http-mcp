#!/bin/bash
# Test ADAM MCP Server in stdio mode

echo "Testing ADAM MCP Server..."
echo "================================"
echo ""

# Test 1: Initialize
echo "Test 1: Initializing MCP session..."
(
  echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
  sleep 1
  echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
  sleep 1
  echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"test_adam_connection","arguments":{}}}'
  sleep 2
) | MCP_TRANSPORT=stdio venv/bin/python server.py 2>/dev/null | grep -A 5 '"result"' | head -30

echo ""
echo "================================"
echo "Test complete!"
