# ADAM MCP Server - Deployment Guide

This guide is for IT administrators deploying the ADAM MCP Server on an Ubuntu server with Apache2.

## Prerequisites

- Ubuntu Server (20.04 LTS or newer)
- Apache2 installed and configured
- SSL certificate for HTTPS
- ADAM API token (30 characters)
- Python 3.10 or newer
- Git (for cloning the repository)
- Root or sudo access

## Installation Steps

### 1. Install Python and Required System Packages

```bash
# Update package list
sudo apt update

# Install Python 3.10+, pip, and git
sudo apt install python3 python3-pip python3-venv git -y

# Verify Python version (should be 3.10 or higher)
python3 --version

# Verify git is installed
git --version
```

### 2. Clone the Repository

```bash
# Navigate to web root directory
cd /var/www

# Clone the repository from GitHub
sudo git clone https://github.com/dominic-gruijters/adam-mcp.git

# Set ownership to www-data (Apache's user)
sudo chown -R www-data:www-data /var/www/adam-mcp
```

**Alternative methods**:

If you prefer SSH (requires SSH key configured on GitHub):
```bash
sudo git clone git@github.com:dominic-gruijters/adam-mcp.git
sudo chown -R www-data:www-data /var/www/adam-mcp
```

Or if you've already downloaded the files:
```bash
sudo cp -r /path/to/adam-mcp /var/www/
sudo chown -R www-data:www-data /var/www/adam-mcp
```

### 3. Set Up Python Virtual Environment

```bash
# Switch to the application directory
cd /var/www/adam-mcp

# Create virtual environment as www-data user
sudo -u www-data python3 -m venv venv

# Activate virtual environment
sudo -u www-data venv/bin/pip install --upgrade pip

# Install dependencies
sudo -u www-data venv/bin/pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
sudo -u www-data cp .env.example .env

# Edit the .env file with your credentials
sudo -u www-data nano .env
```

Configure the following variables in `.env`:

```bash
# Your ADAM API token (30 characters)
ADAM_API_TOKEN=your_30_character_token_here

# Full URL to your ADAM API endpoint (including /api)
# Examples:
#   - https://yourschool.adam.co.za/api
#   - https://adam.yourschool.edu/api
#   - https://sis.yourschool.com/api
ADAM_BASE_URL=https://yourschool.adam.co.za/api

# SSL certificate verification (ALWAYS true in production)
ADAM_VERIFY_SSL=true

# MCP Server settings (defaults are usually fine)
MCP_SERVER_NAME=ADAM School MIS
MCP_HOST=127.0.0.1
MCP_PORT=8000
```

**SSL Certificate Requirements**:
- ✅ Production MUST use valid SSL certificates (Let's Encrypt, commercial CA, etc.)
- ✅ Keep `ADAM_VERIFY_SSL=true` in production for security
- ❌ NEVER use self-signed certificates in production
- ❌ NEVER disable SSL verification (`ADAM_VERIFY_SSL=false`) in production

**Important**: Set proper permissions on the .env file to protect the API token:

```bash
sudo chmod 600 /var/www/adam-mcp/.env
sudo chown www-data:www-data /var/www/adam-mcp/.env
```

### 5. Test the MCP Server

Before setting up the systemd service, test that the server runs correctly:

```bash
# Run as www-data user
sudo -u www-data /var/www/adam-mcp/venv/bin/python /var/www/adam-mcp/server.py
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

Press `Ctrl+C` to stop the test server.

### 6. Install systemd Service

```bash
# Copy service file to systemd directory
sudo cp /var/www/adam-mcp/adam-mcp.service /etc/systemd/system/

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable adam-mcp

# Start the service
sudo systemctl start adam-mcp

# Check service status
sudo systemctl status adam-mcp
```

The service should show as "active (running)".

### 7. Configure Apache2 Reverse Proxy

#### Enable Required Apache Modules

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo a2enmod ssl
```

#### Option A: Add to Existing Virtual Host

If you already have an Apache virtual host for your ADAM instance:

```bash
# Edit your existing virtual host configuration
sudo nano /etc/apache2/sites-available/your-existing-adam-site.conf
```

Add this location block inside your existing `<VirtualHost *:443>` section:

```apache
<Location /adam-mcp>
    ProxyPass http://127.0.0.1:8000/mcp
    ProxyPassReverse http://127.0.0.1:8000/mcp
    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Prefix "/adam-mcp"
    ProxyPass http://127.0.0.1:8000/mcp upgrade=websocket
    ProxyAddHeaders On
</Location>
```

#### Option B: Create New Virtual Host

```bash
# Copy the provided Apache configuration
sudo cp /var/www/adam-mcp/apache2-adam-mcp.conf /etc/apache2/sites-available/adam-mcp.conf

# Edit the configuration with your details
sudo nano /etc/apache2/sites-available/adam-mcp.conf

# Update:
# - ServerName
# - SSL certificate paths
# - Any other domain-specific settings

# Enable the site
sudo a2ensite adam-mcp
```

#### Reload Apache

```bash
# Test Apache configuration
sudo apache2ctl configtest

# If test is successful, reload Apache
sudo systemctl reload apache2
```

### 8. Verify Deployment

#### Test Local Connection

```bash
# Test the local endpoint (basic connectivity)
curl http://127.0.0.1:8000/mcp

# Expected response (this means it's working!):
# {"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept text/event-stream"}}
```

**To properly test the MCP protocol** (requires session initialization):
```bash
# Step 1: Initialize session
curl -v -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'

# Extract the session ID from "Mcp-Session-Id" header, then:

# Step 2: List tools using session ID
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: <session-id-from-step-1>" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# Should return a list of available MCP tools
```

#### Test via Apache Proxy

```bash
# Test the proxied endpoint (basic connectivity)
curl https://yourschool.adam.co.za/adam-mcp

# Same "Not Acceptable" error is expected - means Apache proxy is working!
```

#### Test from Claude Desktop

1. Configure Claude Desktop with your server URL:

   **Production with HTTPS** (recommended):
   ```json
   {
     "mcpServers": {
       "adam": {
         "command": "npx",
         "args": ["-y", "mcp-remote", "https://yourschool.adam.co.za/adam-mcp"]
       }
     }
   }
   ```

   **If testing with HTTP** (development only):
   ```json
   {
     "mcpServers": {
       "adam": {
         "command": "npx",
         "args": ["-y", "mcp-remote", "http://yourschool.adam.co.za/adam-mcp", "--allow-http"]
       }
     }
   }
   ```

   **Important**:
   - Always use HTTPS in production (requires SSL certificate configured in Apache2)
   - HTTP requires the `--allow-http` flag (except for localhost)
   - This uses the `mcp-remote` package to connect to HTTP-based MCP servers

2. Restart Claude Desktop

3. Look for the hammer icon (🔨)

4. Ask Claude: "Test the ADAM connection"

## Maintenance

### View Service Logs

```bash
# View recent logs
sudo journalctl -u adam-mcp -n 50

# Follow logs in real-time
sudo journalctl -u adam-mcp -f

# View Apache error logs
sudo tail -f /var/log/apache2/adam-mcp-error.log
```

### Restart the Service

```bash
sudo systemctl restart adam-mcp
```

### Update the Server

When a new version is released on GitHub:

```bash
# Stop the service
sudo systemctl stop adam-mcp

# Navigate to the project directory
cd /var/www/adam-mcp

# Stash any local changes (if you've made custom modifications)
sudo -u www-data git stash

# Pull latest code from GitHub
sudo -u www-data git pull origin main

# Apply stashed changes if needed
# sudo -u www-data git stash pop

# Update dependencies if requirements.txt changed
sudo -u www-data venv/bin/pip install --upgrade -r requirements.txt

# Start the service
sudo systemctl start adam-mcp

# Check that it started successfully
sudo systemctl status adam-mcp
```

**Note**: If you've made custom modifications to the code, consider using branches or forks to manage your changes.

### Check Service Status

```bash
sudo systemctl status adam-mcp
```

## Security Considerations

### API Token Security

- Store API token only in `/var/www/adam-mcp/.env`
- Set file permissions to 600 (readable only by owner)
- Never commit .env to version control
- Use a dedicated ADAM API token for this service
- Regularly rotate the API token

### Network Security

- The MCP server binds to 127.0.0.1 (localhost only)
- Only accessible via Apache reverse proxy
- All external access is over HTTPS
- Consider IP whitelisting in Apache configuration if needed:

```apache
<Location /adam-mcp>
    # ... other directives ...

    # Only allow from specific IP ranges
    Require ip 192.168.1.0/24
    Require ip 10.0.0.0/8
</Location>
```

### Firewall Configuration

```bash
# Ensure only ports 80 and 443 are open externally
sudo ufw status

# Port 8000 should NOT be accessible externally
# It should only accept connections from localhost
```

## Troubleshooting

### Service Won't Start

```bash
# Check service status
sudo systemctl status adam-mcp

# View detailed logs
sudo journalctl -u adam-mcp -n 100

# Common issues:
# - Missing .env file
# - Invalid API token
# - Port 8000 already in use
# - Python dependencies not installed
```

### Apache Proxy Not Working

```bash
# Check Apache error logs
sudo tail -f /var/log/apache2/error.log

# Verify proxy modules are enabled
sudo apache2ctl -M | grep proxy

# Test Apache configuration
sudo apache2ctl configtest
```

### Connection Refused

- Verify MCP service is running: `sudo systemctl status adam-mcp`
- Check that service is listening: `sudo netstat -tlnp | grep 8000`
- Verify firewall rules: `sudo ufw status`

### Invalid API Token

- Verify token is exactly 30 characters
- Check token has proper permissions in ADAM admin panel
- Test token directly with ADAM API

## Performance Tuning

### Systemd Service

For high-traffic environments, consider adjusting the service configuration:

```ini
[Service]
# Limit memory usage
MemoryMax=512M

# Set CPU priority
CPUWeight=100

# Restart limits
StartLimitBurst=5
StartLimitIntervalSec=60
```

### Apache Configuration

For better performance with many concurrent connections:

```apache
<Location /adam-mcp>
    # Connection pooling
    ProxyPass http://127.0.0.1:8000/mcp connectiontimeout=5 timeout=300 max=20
    # ... other directives ...
</Location>
```

## Getting the ADAM API Token

1. Log into ADAM as an administrator
2. Navigate to: **Administration → Security Administration → Manage API Tokens**
3. Click "Add New Token" or use an existing one
4. Assign permissions for required resources:
   - Pupils (read)
   - Families (read)
   - Classes (read)
   - Reporting (read)
   - Absentees (read)
   - APIRequests (for testing)
5. Copy the 30-character token

## Support and Resources

- ADAM API Documentation: https://help.adam.co.za/api-access-to-adam.html
- Model Context Protocol: https://modelcontextprotocol.io
- FastMCP Documentation: https://github.com/jlowin/fastmcp

## Version Information

- MCP Server Version: 1.0.0
- Supported ADAM API Version: Current
- Python Requirements: 3.10+
- Supported OS: Ubuntu 20.04+
