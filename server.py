"""ADAM MCP Server - Model Context Protocol server for ADAM School MIS."""

from fastmcp import FastMCP
from adam_api import AdamAPIClient, AdamAPIError
from config import Config

# Initialize FastMCP server
mcp = FastMCP(
    name=Config.MCP_SERVER_NAME,
    version=Config.MCP_SERVER_VERSION,
)

# Initialize ADAM API client
api_client = AdamAPIClient()


# ============================================================================
# PUPIL INFORMATION TOOLS
# ============================================================================


@mcp.tool()
async def get_pupil_information(pupil_id: str) -> str:
    """
    Get comprehensive information about a pupil.

    This retrieves basic pupil information including their name, grade,
    boarding house, medical aid details, and other essential information.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with pupil information
    """
    try:
        result = await api_client.get_pupil_info(pupil_id)
        return f"Pupil Information:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving pupil information: {e.message}"


@mcp.tool()
async def get_pupil_classes(pupil_id: str) -> str:
    """
    Get a list of all classes that a pupil is enrolled in.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with class list
    """
    try:
        result = await api_client.get_pupil_classes(pupil_id)
        return f"Pupil Classes:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving classes: {e.message}"


# ============================================================================
# ACADEMIC RECORDS TOOLS
# ============================================================================


@mcp.tool()
async def get_pupil_academic_record(pupil_id: str) -> str:
    """
    Get academic records and marks for a pupil across all reporting periods.

    This retrieves the pupil's marks, grades, and assessment results
    organized by reporting period and subject.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with academic records by period and subject
    """
    try:
        result = await api_client.get_pupil_academic_records(pupil_id)
        return f"Academic Records:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving academic records: {e.message}"


# ============================================================================
# TEACHER AND CONTACT INFORMATION TOOLS
# ============================================================================


@mcp.tool()
async def get_pupil_teachers_emails(pupil_id: str) -> str:
    """
    Get a list of all teachers for a pupil, including their email addresses.

    This is useful for contacting all of a pupil's teachers.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with teacher names and email addresses
    """
    try:
        result = await api_client.get_pupil_teachers(pupil_id)
        return f"Pupil's Teachers:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving teacher information: {e.message}"


@mcp.tool()
async def get_pupil_classes_and_teachers(pupil_id: str) -> str:
    """
    Get a list of all classes and their teachers for a pupil.

    This shows which teacher teaches each class that the pupil is enrolled in.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with class names and teacher names
    """
    try:
        result = await api_client.get_pupil_teachers(pupil_id)
        return f"Pupil's Classes and Teachers:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving classes and teachers: {e.message}"


@mcp.tool()
async def get_all_family_contact_list() -> str:
    """
    Get contact list of all families in the system.

    This returns contact information including names, emails, and phone numbers
    for all family records.

    Returns:
        Formatted string with all family contact information
    """
    try:
        result = await api_client.get_all_family_contacts()
        return f"Family Contact List:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving family contacts: {e.message}"


@mcp.tool()
async def get_family_emails(family_id: str) -> str:
    """
    Get email addresses for a specific family.

    Args:
        family_id: The family ID

    Returns:
        Formatted string with family email addresses
    """
    try:
        result = await api_client.get_family_emails(family_id)
        return f"Family Email Addresses:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving family emails: {e.message}"


# ============================================================================
# NAME-BASED LOOKUP TOOLS
# ============================================================================


@mcp.tool()
async def find_pupil_by_name(name: str) -> str:
    """
    Search for pupils by name (first name, last name, or preferred name).

    This tool enables finding pupil IDs by searching with partial or full names.
    Use the returned pupil_id with other tools like get_pupil_information.

    Args:
        name: Name to search for (case-insensitive, partial matches supported)
              Examples: "Smith", "John", "John Smith", "Arde"

    Returns:
        Formatted list of matching pupils with their IDs, names, grades, and admin numbers
    """
    try:
        results = await api_client.find_pupils_by_name(name)
        if not results:
            return f"No pupils found matching '{name}'"

        output = f"Found {len(results)} pupil(s) matching '{name}':\n\n"
        for i, pupil in enumerate(results, 1):
            output += f"{i}. {pupil['preferred_name']} {pupil['last_name']}\n"
            output += f"   Pupil ID: {pupil['pupil_id']}\n"
            output += f"   Admin Number: {pupil['admin_number']}\n"
            output += f"   Grade: {pupil['grade']}\n"
            output += f"   Email: {pupil['email']}\n"
            output += "\n"

        output += "Use the Pupil ID with other tools like get_pupil_information(pupil_id)"
        return output
    except AdamAPIError as e:
        return f"Error searching for pupils: {e.message}"


@mcp.tool()
async def find_family_by_name(name: str) -> str:
    """
    Search for families by family surname or parent names.

    This tool enables finding family IDs by searching with partial or full names.
    Use the returned family_id with other tools like get_family_emails.

    Args:
        name: Name to search for (case-insensitive, partial matches supported)
              Examples: "Smith", "Anderson", "John"

    Returns:
        Formatted list of matching families with their IDs and names
    """
    try:
        results = await api_client.find_families_by_name(name)
        if not results:
            return f"No families found matching '{name}'"

        output = f"Found {len(results)} family/families matching '{name}':\n\n"
        for i, family in enumerate(results, 1):
            output += f"{i}. {family['family_surname']}\n"
            output += f"   Family ID: {family['family_id']}\n"
            output += f"   Address Name: {family['address_name']}\n"
            output += f"   First Names: {family['family_first_names']}\n"
            if family['father_greeting']:
                output += f"   Father: {family['father_greeting']}\n"
            if family['mother_greeting']:
                output += f"   Mother: {family['mother_greeting']}\n"
            output += "\n"

        output += "Use the Family ID with other tools like get_family_emails(family_id)"
        return output
    except AdamAPIError as e:
        return f"Error searching for families: {e.message}"


@mcp.tool()
async def find_staff_by_name(name: str) -> str:
    """
    Search for staff members by name (first name, last name, or preferred name).

    This tool enables finding staff IDs by searching with partial or full names.

    Args:
        name: Name to search for (case-insensitive, partial matches supported)
              Examples: "Smith", "Jane", "Abbott"

    Returns:
        Formatted list of matching staff members with their IDs, names, positions, and contact info
    """
    try:
        results = await api_client.find_staff_by_name(name)
        if not results:
            return f"No staff members found matching '{name}'"

        output = f"Found {len(results)} staff member(s) matching '{name}':\n\n"
        for i, staff in enumerate(results, 1):
            output += f"{i}. {staff['full_name']}\n"
            output += f"   Staff ID: {staff['staff_id']}\n"
            output += f"   Admin No: {staff['admin_no']}\n"
            output += f"   Position: {staff['position']}\n"
            if staff['department']:
                output += f"   Department: {staff['department']}\n"
            output += f"   Email: {staff['email']}\n"
            output += "\n"

        return output
    except AdamAPIError as e:
        return f"Error searching for staff: {e.message}"


# ============================================================================
# CLASS AND PARENT CONTACT TOOLS
# ============================================================================


@mcp.tool()
async def list_classes_for_grade(grade: str) -> str:
    """
    List all available classes for a specific grade.

    Use this tool first to see what class descriptions are available before
    calling get_class_parent_emails.

    Args:
        grade: Grade level (e.g., "8", "9", "10", "11", "12")

    Returns:
        List of all class descriptions available for that grade
    """
    try:
        registrations_response = await api_client.get_grade_registrations(grade)

        # Handle response - could be a list or dict with 'data' key
        if isinstance(registrations_response, dict):
            registrations_data = registrations_response.get("data", registrations_response)
        else:
            registrations_data = registrations_response

        if not registrations_data or not isinstance(registrations_data, list):
            return f"No registrations found for grade {grade}"

        # Collect unique class descriptions
        classes = {}
        for reg in registrations_data:
            class_desc = reg.get("class_description", "")
            class_id = reg.get("class_id")
            subject = reg.get("subject_name", "")

            if class_desc and class_desc not in classes:
                classes[class_desc] = {
                    "class_id": class_id,
                    "subject": subject,
                    "pupil_count": 0
                }
            if class_desc:
                classes[class_desc]["pupil_count"] += 1

        if not classes:
            return f"No classes found for grade {grade}"

        output = f"Available Classes for Grade {grade}:\n"
        output += "=" * 60 + "\n\n"

        for i, (class_desc, info) in enumerate(sorted(classes.items()), 1):
            output += f"{i}. {class_desc}\n"
            output += f"   Subject: {info['subject']}\n"
            output += f"   Pupils: {info['pupil_count']}\n"
            output += f"   Class ID: {info['class_id']}\n\n"

        output += f"\nTotal: {len(classes)} unique classes\n"
        output += f"\nUse these class descriptions with get_class_parent_emails()\n"
        output += f"Example: get_class_parent_emails('{grade}', 'Mathematics')"

        return output

    except AdamAPIError as e:
        return f"Error retrieving classes: {e.message}"


@mcp.tool()
async def get_class_parent_emails(grade: str, class_description: str) -> str:
    """
    Get all parent email addresses for pupils in a specific class.

    This is useful for teachers who want to email all parents in their class.
    Searches by class description (e.g., "Mathematics", "English", "10A").

    Args:
        grade: Grade level (e.g., "8", "9", "10", "11", "12")
        class_description: Class description to search for (partial match, case-insensitive)
                          Examples: "Mathematics", "English", "10A", "Biology"

    Returns:
        Formatted string with both a comma-separated email list and detailed breakdown
    """
    try:
        result = await api_client.get_class_parent_emails(grade, class_description)

        summary = result["summary"]
        all_emails = result["all_emails"]
        pupils = result["pupils"]

        if summary["total_pupils"] == 0:
            return f"No classes found matching '{class_description}' in grade {grade}"

        # Build output with both formats
        output = f"Parent Emails for Grade {grade} - '{class_description}'\n"
        output += "=" * 60 + "\n\n"

        # Show matched class names
        if summary["matched_class_names"]:
            output += f"Matched Classes: {', '.join(summary['matched_class_names'])}\n\n"

        # Format 1: Comma-separated list (ready to copy-paste)
        output += "=== COMMA-SEPARATED EMAIL LIST (Copy for Email) ===\n"
        output += ", ".join(all_emails) + "\n\n"

        # Format 2: Detailed breakdown
        output += "=== DETAILED BREAKDOWN BY PUPIL ===\n\n"
        for i, pupil in enumerate(pupils, 1):
            output += f"{i}. {pupil['pupil_firstname']} {pupil['pupil_lastname']}"
            output += f" (ID: {pupil['pupil_id']}, Admin: {pupil['pupil_admin']})\n"
            output += f"   Class: {pupil['class_description']}\n"

            if pupil["families"]:
                for family in pupil["families"]:
                    output += f"   Family: {family['family_name']} (ID: {family['family_id']})\n"
                    output += f"   Relationship: {family['relationship']}\n"
                    if family["emails"]:
                        output += f"   Emails: {', '.join(family['emails'])}\n"
                    else:
                        output += "   Emails: (none on record)\n"
            else:
                output += "   Families: (none on record)\n"
            output += "\n"

        # Summary statistics
        output += "=" * 60 + "\n"
        output += f"SUMMARY:\n"
        output += f"  Total Pupils: {summary['total_pupils']}\n"
        output += f"  Total Families: {summary['total_families']}\n"
        output += f"  Total Unique Email Addresses: {summary['total_emails']}\n"

        return output

    except AdamAPIError as e:
        return f"Error retrieving class parent emails: {e.message}"


# ============================================================================
# ATTENDANCE TOOLS
# ============================================================================


@mcp.tool()
async def get_absence_summary(start_date: str, end_date: str) -> str:
    """
    Get a summary of pupil absences for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format (e.g., "2024-01-01")
        end_date: End date in YYYY-MM-DD format (e.g., "2024-01-31")

    Returns:
        Formatted string with absence summary counts
    """
    try:
        result = await api_client.get_absence_summary(start_date, end_date)
        return f"Absence Summary ({start_date} to {end_date}):\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving absence summary: {e.message}"


@mcp.tool()
async def get_detailed_absence_list(start_date: str, end_date: str) -> str:
    """
    Get a detailed list of all absences with reasons for a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format (e.g., "2024-01-01")
        end_date: End date in YYYY-MM-DD format (e.g., "2024-01-31")

    Returns:
        Formatted string with detailed absence records
    """
    try:
        result = await api_client.get_absence_list(start_date, end_date)
        return f"Detailed Absence List ({start_date} to {end_date}):\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving absence list: {e.message}"


# ============================================================================
# UTILITY TOOLS
# ============================================================================


@mcp.tool()
async def test_adam_connection() -> str:
    """
    Test the connection to ADAM API.

    Use this to verify that the MCP server can successfully connect to
    the ADAM API and that the API token is valid.

    Returns:
        Status message indicating success or failure
    """
    result = await api_client.test_connection()
    if result["success"]:
        return f"✓ Connection successful! ADAM API is accessible.\n{_format_json(result.get('data', {}))}"
    else:
        return f"✗ Connection failed: {result['message']}"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _format_json(data: dict) -> str:
    """
    Format JSON data for readable output.

    Args:
        data: Dictionary to format

    Returns:
        Formatted string representation
    """
    import json

    return json.dumps(data, indent=2, ensure_ascii=False)


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================


if __name__ == "__main__":
    # Run the MCP server with Streamable HTTP transport
    # The server will be available at http://localhost:8000/mcp
    print(f"Starting {Config.MCP_SERVER_NAME} v{Config.MCP_SERVER_VERSION}")
    print(f"Server will listen on {Config.MCP_HOST}:{Config.MCP_PORT}")
    print(f"Connecting to ADAM API: {Config.ADAM_BASE_URL}")
    print("\nAvailable endpoints:")
    print(f"  - Streamable HTTP: http://{Config.MCP_HOST}:{Config.MCP_PORT}/mcp")
    print("\nPress Ctrl+C to stop the server\n")

    # Run with FastMCP using Streamable HTTP transport
    # FastMCP automatically creates the /mcp endpoint with Streamable HTTP transport
    mcp.run(transport="http", host=Config.MCP_HOST, port=Config.MCP_PORT)
