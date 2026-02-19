# ADAM CLI

Command-line interface for the ADAM School Management Information System. Query pupil info, academic records, attendance, and contacts from the terminal. Outputs JSON by default for piping and scripting.

## Installation

```bash
pipx install -e .
```

This installs the `adam` command in an isolated environment via [pipx](https://pipx.pypa.io/).

## Authentication

Set your credentials:

```bash
export ADAM_API_TOKEN=your_30_character_token_here
export ADAM_BASE_URL=https://yourschool.adam.co.za/api
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

## Usage

```bash
# Test connection
adam test

# Pupils
adam pupils find Smith
adam pupils info 12345
adam pupils classes 12345
adam pupils contacts
adam pupils search-id 0001010000001
adam pupils fields edit
adam pupils search-admin 2024001

# Calendar
adam calendar pupil-links
adam calendar staff-links

# Academic records
adam academics record 12345
adam academics assessments 12345
adam academics markbook 1 12345
adam academics periods 2024
adam academics pupil-periods 12345
adam academics results 1
adam academics previous-reports 12345
adam academics question-breakdown 456

# Teachers
adam teachers emails 12345
adam teachers classes 12345

# Families
adam families find Smith
adam families emails 67890
adam families children 67890
adam families current-children 67890
adam families relationships 12345
adam families family-relationships 67890
adam families contacts
adam families search-id 8001015678081
adam families relationship-types
adam families login-privileges 67890

# Classes
adam classes list 10
adam classes parent-emails 10 Mathematics
adam classes by-grade-period-subject 10 1 1

# Attendance
adam attendance summary 2024-01-01 2024-01-31
adam attendance list 2024-01-01 2024-01-31
adam attendance pupil-days 12345 2024

# Leaves
adam leaves approved 2024-03-01 2024-03-31

# Records (behaviour/achievements)
adam records recent 12345
adam records by-date 12345 2024-01-01 2024-06-30

# Staff
adam staff find Jones

# Medical
adam medical off-sport
adam medical off-sport 2024-03-15

# Subjects
adam subjects by-grade 10
adam subjects by-grades 8,9,10

# Psychometric
adam psychometric assessments 12345

# Messages
adam messages list 2024-03-01 2024-03-31
adam messages get 1

# Admissions
adam admissions status-list
adam admissions statuses

# Data Query
adam dataquery get-one your_secret 42
```

### Output formats

```bash
adam pupils find Smith                    # JSON (default)
adam pupils find Smith --format text      # human-readable
adam pupils find Smith --format csv       # CSV export
```

### Piping

```bash
adam pupils find Smith | jq -r '.[0].pupil_id' | xargs adam academics record
adam classes parent-emails 10 Mathematics | jq -r '.all_emails[]'
adam attendance list 2024-01-01 2024-01-31 | jq -r '.[].pupil_id' | sort -u
```

## Commands

| Group | Command | Description |
|-------|---------|-------------|
| `test` | | Test API connection |
| `pupils` | `find <name>` | Search pupils by name |
| | `info <id>` | Get pupil details |
| | `classes <id>` | Get pupil's classes and teachers |
| | `contacts` | Get all pupil contacts |
| | `search-id <id_number>` | Search pupil by ID number |
| | `fields [action]` | Get pupil field definitions |
| | `search-admin <term>` | Search pupils by admin identifier |
| `calendar` | `pupil-links` | Get pupil calendar links |
| | `staff-links` | Get staff calendar links |
| `academics` | `record <id>` | Get academic records |
| | `assessments <id>` | Get recent assessment results |
| | `markbook <period> <id>` | Get markbook for a period |
| | `periods [year]` | Get reporting periods |
| | `pupil-periods <id>` | Get reporting periods for a pupil |
| | `results <period>` | Get all results for a period |
| | `previous-reports <id>` | Get list of previous reports |
| | `question-breakdown <assessment>` | Get question breakdown for an assessment |
| `teachers` | `emails <id>` | Get pupil's teachers and emails |
| | `classes <id>` | Get pupil's classes with teachers |
| `families` | `find <name>` | Search families by name |
| | `emails <family_id>` | Get family email addresses |
| | `children <family_id>` | Get children in a family |
| | `current-children <family_id>` | Get currently enrolled children |
| | `relationships <id>` | Get family relationships for a pupil |
| | `family-relationships <family_id>` | Get relationship details for a family |
| | `contacts` | Get all family contacts |
| | `search-id <id_number>` | Search family by ID number |
| | `relationship-types` | Get relationship type definitions |
| | `login-privileges <family_id>` | Get family login privileges |
| `classes` | `list <grade>` | List classes for a grade |
| | `parent-emails <grade> <class>` | Get parent emails for a class |
| | `by-grade-period-subject <g> <p> <s>` | Get classes by grade, period, subject |
| `attendance` | `summary <from> <to>` | Get absence summary |
| | `list <from> <to>` | Get detailed absence list |
| | `pupil-days <id> [year]` | Get days absent for a pupil |
| `leaves` | `approved [from] [to]` | Get approved leave requests |
| `records` | `recent <id>` | Get recent behaviour records |
| | `by-date <id> [from] [to]` | Get records by date range |
| `staff` | `find <name>` | Search staff by name |
| `medical` | `off-sport [date]` | Get off-sport list |
| `subjects` | `by-grade <grade>` | Get subjects for a grade |
| | `by-grades <grades>` | Get subjects for multiple grades |
| `psychometric` | `assessments [pupil] [category]` | Get psychometric assessments |
| `messages` | `list [from] [to]` | Get messaging logs |
| | `get <message_id>` | Get a specific message |
| `admissions` | `status-list` | Get registration status types |
| | `statuses` | Get all pupil registration statuses |
| `dataquery` | `get-one <secret> <id>` | Get single record from data query |

## License

This project is intended for use with ADAM School MIS installations. Review your ADAM license agreement regarding API usage.
