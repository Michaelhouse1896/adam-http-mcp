# CLAUDE.md

## Project Overview

HTTP MCP server for the ADAM School Management Information System REST API. Exposes ADAM endpoints as MCP tools over HTTP using StreamableHTTPServerTransport. Teachers and AI agents query pupil info, academic records, attendance, and contacts.

**Stack**: TypeScript / Express / @modelcontextprotocol/sdk. Two source files: `src/tools.ts` (tool definitions) + `src/index.ts` (server, API client, custom handlers).

## Development Commands

```bash
# Install dependencies
npm install

# Development (no build needed, uses tsx)
npm run dev

# Build to dist/
npm run build

# Run production build
npm start

# Set credentials via environment
export ADAM_API_TOKEN=your_30_character_token_here
export ADAM_BASE_URL=https://yourschool.adam.co.za/api
export PORT=3000
```

**No tests, linting, or formatting tools are configured.**

## Architecture

### src/tools.ts — Tool Definitions

Array of `ToolDef` objects. Each defines:
- `toolName` — MCP tool name (e.g. `pupils_find`, `academics_record`)
- `description` — Human-readable description
- `params` — Array of `{name, type, required, description}`
- `module` / `resource` / `pathParams` — For simple tools that map directly to ADAM API paths
- `handler: "custom"` — For tools that need custom logic

### src/index.ts — Server

1. **Config** — Reads env vars, validates token (30 chars) and base URL
2. **adamRequest()** — Central API caller. Builds URL: `{BASE_URL}/{module}/{resource}/{p1}/{p2}/...`. Unwraps ADAM's `{"response": {"code": 200}, "data": ...}` wrapper.
3. **buildZodShape()** — Converts tool params to Zod schemas for MCP registration
4. **callSimpleTool()** — Generic handler for tools with `module`/`resource`/`pathParams`
5. **Custom handlers** — `handlePupilsFind`, `handleFamiliesFind`, `handleStaffFind`, `handleClassesList`, `handleClassesParentEmails`, `handleLeavesApproved`
6. **createServer()** — Registers all tools from `tools.ts` as MCP tools
7. **Express transport** — POST/GET/DELETE on `/mcp` with per-session isolation

### ADAM API URL Pattern

All parameters are **path segments**, not query params: `/api/{module}/{resource}/{param1}/{param2}/...`

Parameters are percent-encoded. Dates must be `YYYY-MM-DD`.

### Custom Handler Tools

- **pupils_find / families_find / staff_find** — Fetch all data via Data Query API, client-side multi-word name filtering
- **classes_list** — Aggregates grade registrations into deduplicated class summary
- **classes_parent_emails** — Chains: grade registrations → family relationships → family emails → deduplicated email list
- **leaves_approved** — Client-side date range filtering

## Adding a New Tool

1. Add entry to `tools` array in `src/tools.ts`:
   ```typescript
   {
     toolName: "group_action",
     description: "What it does",
     params: [{ name: "param", type: "string", required: true, description: "..." }],
     module: "ModuleName",
     resource: "resource",
     pathParams: ["param"],
   }
   ```

2. For complex tools, set `handler: "custom"` and add handler function + dispatch entry in `src/index.ts`.

3. Reference `API_DOCUMENTATION.md` for endpoint details (70+ endpoints documented).

## Configuration

All via environment variables:
- **Required**: `ADAM_API_TOKEN` (30 chars), `ADAM_BASE_URL` (full URL ending in `/api`)
- **Optional**: `ADAM_DATAQUERY_PUPILS_SECRET`, `ADAM_DATAQUERY_FAMILIES_SECRET`, `ADAM_DATAQUERY_STAFF_SECRET` (enable name lookups), `ADAM_VERIFY_SSL` (default `true`), `PORT` (default `3000`)

## MCP Client Configuration

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

## Docker

```bash
docker build -t adam-http-mcp .
docker run -p 3000:3000 \
  -e ADAM_API_TOKEN=your_token \
  -e ADAM_BASE_URL=https://yourschool.adam.co.za/api \
  adam-http-mcp
```
