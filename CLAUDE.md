# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pure CLI tool for the ADAM School Management Information System REST API. Teachers query pupil info, academic records, attendance, and contacts via command line. Designed for piping, scripting, and agent use (OpenClaw etc.).

**Stack**: Python 3.10+ / httpx. Installed via `pipx install -e .`.

## Development Commands

```bash
# Install (isolated env via pipx)
pipx install -e .

# Set credentials via environment
export ADAM_API_TOKEN=your_30_character_token_here
export ADAM_BASE_URL=https://yourschool.adam.co.za/api

# Run
adam test
adam pupils find Smith
adam academics periods 2024 --format text

# Piping
adam pupils find Smith | jq -r '.[0].pupil_id' | xargs adam academics record
adam classes parent-emails 10 Mathematics | jq -r '.all_emails[]'
```

## Architecture

Single-file Python CLI (`adam_cli.py`) containing everything:

- **Config class** — reads env vars, validates token (30 chars) and base URL
- **AdamAPIClient class** — all async ADAM API methods. Central `_make_request(module, resource, params)` builds path-segment URLs: `/api/{module}/{resource}/{param1}/{param2}`. Parameters are percent-encoded.
- **AdamAPIError** — custom exception with message and status_code
- **CLI** — argparse with nested subparsers, 28 commands in 10 groups
- **Output formatters** — json (default), text, csv

`pyproject.toml` defines the `adam` console script entry point and `httpx` dependency. Installed via `pipx install -e .` for an isolated environment.

### ADAM API URL Pattern

```
/api/pupils/pupil/12345              (NOT ?id=12345)
/api/absentees/summarycount/2024-01-01/2024-01-31   (NOT ?from=...&to=...)
```

All parameters are path segments joined by `/`, percent-encoded.

### Data Flow for Name-Based Lookups

`find_pupils_by_name` -> `get_all_pupils_data()` (Data Query API with secret) -> client-side filter. Same for families and staff. Requires `ADAM_DATAQUERY_*_SECRET` env vars.

### Data Flow for Class Parent Emails

`get_class_parent_emails` orchestrates: grade registrations -> filter by class description -> per-pupil family relationships -> per-family emails -> deduplicate.

## Adding a New CLI Command

1. Add async method to `AdamAPIClient`:
   ```python
   async def get_something(self, param: str) -> dict[str, Any]:
       return await self._make_request("ModuleName", "resource", [param])
   ```

2. Add command handler:
   ```python
   async def cmd_group_action(client: AdamAPIClient, args: argparse.Namespace) -> Any:
       return await client.get_something(args.param)
   ```

3. Add subparser in `build_parser()`:
   ```python
   p = group_sub.add_parser("action", help="Description")
   p.add_argument("param", help="Parameter description")
   p.set_defaults(func=cmd_group_action)
   ```

4. Reference `API_DOCUMENTATION.md` for endpoint details. Dates must be `YYYY-MM-DD`.

## CLI Command Tree

```
adam test
adam pupils find|info|classes|contacts|search-id|fields|search-admin
adam calendar pupil-links|staff-links
adam academics record|assessments|markbook|periods|pupil-periods|results|previous-reports|question-breakdown
adam teachers emails|classes
adam families find|emails|children|relationships|contacts|current-children|search-id|relationship-types|family-relationships|login-privileges
adam classes list|parent-emails|by-grade-period-subject
adam attendance summary|list|pupil-days
adam leaves approved
adam records recent|by-date
adam staff find
adam medical off-sport
adam subjects by-grade|by-grades
adam psychometric assessments
adam messages list|get
adam admissions status-list|statuses
adam dataquery get-one
```

All output JSON to stdout by default. `--format text` for humans. `--format csv` for export. Errors to stderr. Exit 0/1.

## Configuration

All via environment variables (`export`). Required: `ADAM_API_TOKEN` (30 chars), `ADAM_BASE_URL` (full URL ending in `/api`). Optional: `ADAM_DATAQUERY_PUPILS_SECRET`, `ADAM_DATAQUERY_FAMILIES_SECRET`, `ADAM_DATAQUERY_STAFF_SECRET` (enable name lookups), `ADAM_VERIFY_SSL` (default `true`).
