# ADAM HTTP MCP

HTTP MCP server for the ADAM School Management Information System. Exposes 47 ADAM API endpoints as MCP tools over HTTP using StreamableHTTPServerTransport. Designed for AI agents, Claude Desktop, and any MCP client.

## Quick Start

```bash
npm install
npm run dev
```

The server listens on `http://localhost:3000/mcp`.

## Configuration

Set credentials via environment variables:

```bash
export ADAM_API_TOKEN=your_30_character_token_here
export ADAM_BASE_URL=https://yourschool.adam.co.za/api
export PORT=3000  # optional, default 3000
```

Get your API token from: Administration > Security Administration > Manage API Tokens.

### Optional: name-based lookups

To search pupils, families, and staff by name, set Data Query secrets (from Administration > Data Query):

```bash
export ADAM_DATAQUERY_PUPILS_SECRET=your_pupils_secret
export ADAM_DATAQUERY_FAMILIES_SECRET=your_families_secret
export ADAM_DATAQUERY_STAFF_SECRET=your_staff_secret
```

### Optional: SSL verification

```bash
export ADAM_VERIFY_SSL=false   # default: true
```

## MCP Client Configuration

### Claude Desktop / Claude Code

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

## Development

```bash
# Development (no build, uses tsx)
npm run dev

# Build to dist/
npm run build

# Run production build
npm start
```

## Docker

```bash
docker build -t adam-http-mcp .
docker run -p 3000:3000 \
  -e ADAM_API_TOKEN=your_token \
  -e ADAM_BASE_URL=https://yourschool.adam.co.za/api \
  adam-http-mcp
```

## Tools

47 MCP tools across 16 categories:

| Category | Tool | Description |
|----------|------|-------------|
| **Test** | `test_connection` | Test API connectivity |
| **Pupils** | `pupils_find` | Search pupils by name (requires dataquery secret) |
| | `pupils_info` | Get pupil details |
| | `pupils_classes` | Get pupil's classes and teachers |
| | `pupils_contacts` | Get all pupil contacts |
| | `pupils_search_id` | Search pupil by ID number |
| | `pupils_fields` | Get pupil field definitions |
| | `pupils_search_admin` | Search by admin identifier |
| **Calendar** | `calendar_pupil_links` | Get pupil calendar links |
| | `calendar_staff_links` | Get staff calendar links |
| **Academics** | `academics_record` | Get academic records |
| | `academics_assessments` | Get recent assessment results |
| | `academics_markbook` | Get markbook for a period |
| | `academics_periods` | Get reporting periods |
| | `academics_pupil_periods` | Get reporting periods for a pupil |
| | `academics_results` | Get all results for a period |
| | `academics_previous_reports` | Get previous reports |
| | `academics_question_breakdown` | Get question breakdown |
| **Teachers** | `teachers_emails` | Get pupil's teachers and emails |
| | `teachers_classes` | Get pupil's classes with teachers |
| **Families** | `families_find` | Search families by name (requires dataquery secret) |
| | `families_emails` | Get family email addresses |
| | `families_children` | Get children in a family |
| | `families_relationships` | Get family relationships for a pupil |
| | `families_contacts` | Get all family contacts |
| | `families_current_children` | Get currently enrolled children |
| | `families_search_id` | Search family by ID number |
| | `families_relationship_types` | Get relationship type definitions |
| | `families_family_relationships` | Get relationship details for a family |
| | `families_login_privileges` | Get family login privileges |
| **Classes** | `classes_list` | List classes for a grade with pupil counts |
| | `classes_parent_emails` | Get parent emails for a class (multi-step) |
| | `classes_by_grade_period_subject` | Get classes by grade, period, subject |
| **Attendance** | `attendance_summary` | Get absence summary for date range |
| | `attendance_list` | Get detailed absence list |
| | `attendance_pupil_days` | Get days absent for a pupil |
| **Leaves** | `leaves_approved` | Get approved leave requests |
| **Records** | `records_recent` | Get recent behaviour records |
| | `records_by_date` | Get records by date range |
| **Staff** | `staff_find` | Search staff by name (requires dataquery secret) |
| **Medical** | `medical_off_sport` | Get off-sport list |
| **Subjects** | `subjects_by_grade` | Get subjects for a grade |
| | `subjects_by_grades` | Get subjects for multiple grades |
| **Psychometric** | `psychometric_assessments` | Get psychometric assessments |
| **Messages** | `messages_list` | Get messaging logs |
| | `messages_get` | Get a specific message |
| **Admissions** | `admissions_status_list` | Get registration status types |
| | `admissions_statuses` | Get all registration statuses |
| **Data Query** | `dataquery_get_one` | Get single record by secret and ID |

## Architecture

```
src/
  tools.ts    # Tool definitions (names, params, API path mappings)
  index.ts    # MCP server, Express HTTP transport, API client, custom handlers
```

- **Simple tools** map directly to ADAM API paths: `/api/{module}/{resource}/{param1}/{param2}/...`
- **Custom tools** handle complex logic (name searches via Data Query, class parent email orchestration, client-side filtering)
- Per-session isolation via `StreamableHTTPServerTransport`
- ADAM response wrapper (`{"response": {"code": 200}, "data": ...}`) is automatically unwrapped

## License

This project is intended for use with ADAM School MIS installations. Review your ADAM license agreement regarding API usage.
