# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pure CLI tool for the ADAM School Management Information System REST API. Teachers query pupil info, academic records, attendance, and contacts via command line. Designed for piping, scripting, and agent use.

**Stack**: Python 3.10+ / httpx. Single-file CLI (`adam_cli.py`, ~1300 lines) + `pyproject.toml`.

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

# Piping examples
adam pupils find Smith | jq -r '.[0].pupil_id' | xargs adam academics record
adam classes parent-emails 10 Mathematics | jq -r '.all_emails[]'
```

**No tests, linting, or formatting tools are configured.** There is no test suite. Run `adam test` to verify API connectivity.

## Architecture

Everything lives in `adam_cli.py`:

1. **Config** (line ~22) — reads env vars, validates token (exactly 30 chars) and base URL
2. **AdamAPIError** (line ~66) — custom exception with `message` and `status_code`
3. **AdamAPIClient** (line ~73) — all async API methods, central `_make_request()` builds URLs
4. **Output formatters** (line ~576) — `_output_json`, `_output_text`, `_output_csv`
5. **Command handlers** (line ~634) — `cmd_*` async functions, one per CLI command
6. **Parser** (line ~955) — `build_parser()` with argparse nested subparsers
7. **Entry point** (line ~1264) — `_async_main()` → `main()` with SIGPIPE/KeyboardInterrupt handling

### ADAM API URL Pattern

All parameters are **path segments**, not query params. `_make_request(module, resource, params)` builds: `/api/{module}/{resource}/{param1}/{param2}/...`

```
/api/pupils/pupil/12345              (NOT ?id=12345)
/api/absentees/summarycount/2024-01-01/2024-01-31   (NOT ?from=...&to=...)
```

Parameters are percent-encoded via `urllib.parse.quote`. Dates must be `YYYY-MM-DD`.

### API Response Handling

The ADAM API wraps responses in `{"response": {"code": 200}, "data": ...}`. `_make_request()` checks the inner `response.code`, raises `AdamAPIError` on non-200, and returns the unwrapped `data` field. If there's no `response` wrapper, it returns the raw JSON.

### Data Query (Name-Based Lookups)

`find_pupils_by_name`, `find_families_by_name`, `find_staff_by_name` all follow the same pattern:
1. Call `get_all_*_data()` which hits the Data Query API (`dataquery/get/{secret}`)
2. Client-side filter across multiple name fields using multi-word search (`all(word in combined)`)
3. Return a curated subset of fields

Requires `ADAM_DATAQUERY_*_SECRET` env vars. Data Query field names are cryptic (e.g., `last_name_2`, `adam_id_257`) — these come from ADAM's internal schema.

### Complex Orchestration: `get_class_parent_emails`

This is the most complex method (~100 lines). It chains multiple API calls:
grade registrations → filter by class description (case-insensitive substring match) → per-pupil family relationships → per-family emails → deduplicate into `all_emails` list.

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

4. Reference `API_DOCUMENTATION.md` for endpoint details (70+ endpoints documented with paths, parameters, and authorization requirements).

## Configuration

All via environment variables. Required: `ADAM_API_TOKEN` (30 chars), `ADAM_BASE_URL` (full URL ending in `/api`). Optional: `ADAM_DATAQUERY_PUPILS_SECRET`, `ADAM_DATAQUERY_FAMILIES_SECRET`, `ADAM_DATAQUERY_STAFF_SECRET` (enable name lookups), `ADAM_VERIFY_SSL` (default `true`).

## CLI Output

All commands output JSON to stdout by default. `--format text` for human-readable, `--format csv` for export. Errors go to stderr as JSON. Exit code 0 on success, 1 on error, 130 on interrupt. SIGPIPE and BrokenPipeError are handled gracefully for piping to `head`/`less`.
