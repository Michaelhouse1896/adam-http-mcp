# ADAM MCP Server

A Model Context Protocol (MCP) server for ADAM School Management Information System. This server allows teachers and staff to interact with ADAM data through Claude Desktop using natural language.

## Features

Access ADAM data through Claude Desktop with these capabilities:

- **Pupil Search**: Find pupils by name (no need to memorize pupil IDs!)
- **Pupil Information**: Get comprehensive pupil details including boarding house, grade, and medical aid info
- **Class Lists**: Retrieve lists of classes for any pupil
- **Academic Records**: Access marks and grades for specific subjects
- **Report Cards**: View report card comments and summaries
- **Teacher Information**: Get lists of teachers and their email addresses for any pupil
- **Parent Contacts**: Retrieve parent email addresses for entire classes
- **Attendance**: Access absence summaries and detailed absence records

## For Teachers: How to Use

### Prerequisites

- Claude Desktop installed on your computer
- Your school's ADAM MCP server URL (provided by IT administrator)

### Setup Instructions

1. **Open Claude Desktop Configuration**
   - On macOS: Open `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: Open `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add ADAM MCP Server**

   Add the following to your configuration file:

   ```json
   {
     "mcpServers": {
       "adam": {
         "url": "https://yourschool.adam.co.za/adam-mcp"
       }
     }
   }
   ```

   Replace `yourschool.adam.co.za` with your actual ADAM instance URL (your IT admin will provide this).

3. **Restart Claude Desktop**

4. **Verify Connection**

   Look for a hammer icon (🔨) at the bottom-right of Claude Desktop. This indicates that MCP servers are connected.

### Example Queries

Once connected, you can ask Claude things like:

- "Search for pupils named Smith"
- "Find a pupil called John Doe"
- "Get information about pupil with ID 12345"
- "What classes is Sarah enrolled in?" (Claude will search for Sarah first)
- "Show me the Biology marks for pupil 12345"
- "Get all teacher email addresses for pupil 12345"
- "List parent email addresses for class 10A"
- "Show absence summary for January 2024"
- "Get report card comments for pupil 12345"

Claude will use the ADAM MCP server to fetch this information automatically. You can use either pupil names or IDs - Claude will search by name if needed!

## For Developers

See [DEV_SETUP.md](DEV_SETUP.md) for instructions on setting up a local development environment to test and customize the MCP server.

## For IT Administrators

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed server installation and configuration instructions.

## Available Tools

The MCP server provides these tools to Claude:

| Tool | Description |
|------|-------------|
| `search_pupils` | Search for pupils by name |
| `get_pupil_information` | Get comprehensive pupil details |
| `get_pupil_classes` | List classes for a pupil |
| `get_pupil_academic_record` | Get marks and grades (optionally for specific subject) |
| `get_report_card_summary` | View report card comments |
| `get_pupil_teachers_emails` | Get teacher list with email addresses |
| `get_class_parent_emails` | Get parent contacts for a class |
| `get_family_emails` | Get email addresses for a family |
| `get_absence_summary` | Absence counts for a date range |
| `get_detailed_absence_list` | Detailed absence records with reasons |
| `test_adam_connection` | Test API connectivity |

## Security

- The shared school API token is stored securely on the server
- All communication happens over HTTPS
- The MCP server only responds to authenticated requests
- Teachers do not need to manage API tokens individually

## Support

For technical issues or questions:

- Check the [DEPLOYMENT.md](DEPLOYMENT.md) guide for server administration
- Review ADAM API documentation: https://help.adam.co.za/api-access-to-adam.html
- Contact your school's IT administrator

## Version

Current version: 1.0.0

## License

This project is intended for use with ADAM School MIS installations. Please review your ADAM license agreement regarding API usage.
