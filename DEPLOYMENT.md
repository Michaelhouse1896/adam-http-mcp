# ADAM HTTP MCP Server - Deployment Guide

## Prerequisites

- Node.js 22+ (or Docker)
- ADAM API token (30 characters)
- SSL certificate for HTTPS (production)

## Option A: Docker (Recommended)

### 1. Build and Run

```bash
docker build -t adam-http-mcp .
docker run -d \
  --name adam-http-mcp \
  --restart unless-stopped \
  -p 3000:3000 \
  -e ADAM_API_TOKEN=your_30_character_token_here \
  -e ADAM_BASE_URL=https://yourschool.adam.co.za/api \
  -e ADAM_DATAQUERY_PUPILS_SECRET=your_pupils_secret \
  -e ADAM_DATAQUERY_FAMILIES_SECRET=your_families_secret \
  -e ADAM_DATAQUERY_STAFF_SECRET=your_staff_secret \
  adam-http-mcp
```

### 2. Verify

```bash
docker logs adam-http-mcp
# Should show: ADAM MCP server listening on http://0.0.0.0:3000/mcp
```

## Option B: Direct Install

### 1. Clone and Build

```bash
cd /opt
git clone https://github.com/dominic-gruijters/adam-mcp.git adam-http-mcp
cd adam-http-mcp
npm ci
npm run build
```

### 2. Configure Environment

```bash
cat > /opt/adam-http-mcp/.env << 'EOF'
ADAM_API_TOKEN=your_30_character_token_here
ADAM_BASE_URL=https://yourschool.adam.co.za/api
PORT=3000
ADAM_VERIFY_SSL=true
ADAM_DATAQUERY_PUPILS_SECRET=your_pupils_secret
ADAM_DATAQUERY_FAMILIES_SECRET=your_families_secret
ADAM_DATAQUERY_STAFF_SECRET=your_staff_secret
EOF

chmod 600 /opt/adam-http-mcp/.env
```

### 3. Create systemd Service

```bash
cat > /etc/systemd/system/adam-http-mcp.service << 'EOF'
[Unit]
Description=ADAM HTTP MCP Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/adam-http-mcp
EnvironmentFile=/opt/adam-http-mcp/.env
ExecStart=/usr/bin/node /opt/adam-http-mcp/dist/index.js
Restart=on-failure
RestartSec=5
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable adam-http-mcp
systemctl start adam-http-mcp
```

### 4. Verify

```bash
systemctl status adam-http-mcp
journalctl -u adam-http-mcp -f
```

## Reverse Proxy

### Traefik (Docker label)

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.adam-mcp.rule=Host(`adam-mcp.yourschool.co.za`)"
  - "traefik.http.routers.adam-mcp.tls=true"
  - "traefik.http.services.adam-mcp.loadbalancer.server.port=3000"
```

### Apache2

```bash
sudo a2enmod proxy proxy_http headers ssl
```

```apache
<Location /adam-mcp>
    ProxyPass http://127.0.0.1:3000/mcp
    ProxyPassReverse http://127.0.0.1:3000/mcp
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"
</Location>
```

### Nginx

```nginx
location /adam-mcp {
    proxy_pass http://127.0.0.1:3000/mcp;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_set_header Connection '';
    chunked_transfer_encoding off;
    proxy_buffering off;
}
```

## MCP Client Configuration

### Claude Desktop / Claude Code (direct HTTP)

```json
{
  "mcpServers": {
    "adam-school-mis": {
      "type": "streamable-http",
      "url": "http://localhost:3000/mcp"
    }
  }
}
```

### Claude Desktop (via HTTPS proxy with mcp-remote)

```json
{
  "mcpServers": {
    "adam-school-mis": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://adam-mcp.yourschool.co.za/adam-mcp"]
    }
  }
}
```

## Testing the Deployment

```bash
# Basic connectivity (expect "Not Acceptable" error — means it's working)
curl http://127.0.0.1:3000/mcp

# Full MCP session test
curl -X POST http://127.0.0.1:3000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

## Updating

```bash
# Docker
docker stop adam-http-mcp && docker rm adam-http-mcp
git pull origin main
docker build -t adam-http-mcp .
# Re-run docker run command from above

# Direct install
systemctl stop adam-http-mcp
cd /opt/adam-http-mcp
git pull origin main
npm ci
npm run build
systemctl start adam-http-mcp
```

## Maintenance

```bash
# View logs
journalctl -u adam-http-mcp -n 50
journalctl -u adam-http-mcp -f

# Restart
systemctl restart adam-http-mcp

# Docker logs
docker logs -f adam-http-mcp
```

## Security

- Store credentials in `.env` with `chmod 600`
- Bind to localhost only; expose via reverse proxy with HTTPS
- Use a dedicated ADAM API token for this service
- Rotate the API token regularly
- Consider IP whitelisting at the reverse proxy level

## Getting the ADAM API Token

1. Log into ADAM as an administrator
2. Navigate to: **Administration > Security Administration > Manage API Tokens**
3. Create or use an existing token with read permissions for required resources
4. Copy the 30-character token

## Resources

- ADAM API Documentation: https://help.adam.co.za/api-access-to-adam.html
- Model Context Protocol: https://modelcontextprotocol.io
