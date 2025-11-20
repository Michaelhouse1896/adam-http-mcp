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
async def get_pupil_family_relationships(pupil_id: str) -> str:
    """
    Get family relationships and family IDs for a pupil.

    This retrieves information about which families a pupil belongs to,
    including the relationship type (e.g., "Child") and family details.
    Use this to find a pupil's family_id, then use get_family_emails
    to retrieve contact information.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with family relationships including family IDs
    """
    try:
        result = await api_client.get_pupil_family_relationships(pupil_id)
        return f"Pupil's Family Relationships:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving family relationships: {e.message}"


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
# ASSESSMENT AND REPORTING TOOLS
# ============================================================================


@mcp.tool()
async def get_recent_assessment_results(pupil_id: str) -> str:
    """
    Get recent assessment results for a pupil.

    This retrieves the pupil's recent test scores, marks, and assessment comments
    across all subjects.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with recent assessment results
    """
    try:
        result = await api_client.get_recent_assessment_results(pupil_id)
        return f"Recent Assessment Results:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving assessment results: {e.message}"


@mcp.tool()
async def get_pupil_markbook(period_id: str, pupil_id: str) -> str:
    """
    Get detailed markbook/assessment data for a pupil in a specific reporting period.

    This provides a comprehensive breakdown of all assessments, marks, and comments
    organized by subject and assessment category (tests, assignments, exams, etc.).

    Args:
        period_id: The reporting period ID
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with detailed markbook data
    """
    try:
        result = await api_client.get_pupil_markbook(period_id, pupil_id)
        return f"Markbook for Period {period_id}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving markbook: {e.message}"


@mcp.tool()
async def get_reporting_periods(year: str = None) -> str:
    """
    Get all reporting periods (terms/semesters) for a specific year.

    This returns the academic calendar showing all reporting periods with their
    start dates, end dates, and publish dates.

    Args:
        year: Year (e.g., "2024"). If not provided, returns current year's periods.

    Returns:
        Formatted string with reporting periods
    """
    try:
        result = await api_client.get_reporting_periods(year)
        year_str = year if year else "current year"
        return f"Reporting Periods for {year_str}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving reporting periods: {e.message}"


@mcp.tool()
async def get_pupil_reporting_periods(pupil_id: str) -> str:
    """
    Get reporting periods available for a specific pupil.

    This shows which reporting periods the pupil has been enrolled for, including
    their results and report availability.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with pupil's reporting periods
    """
    try:
        result = await api_client.get_pupil_reporting_periods(pupil_id)
        return f"Reporting Periods for Pupil:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving pupil reporting periods: {e.message}"


@mcp.tool()
async def get_pupil_report_pdf_info(period_id: str, pupil_id: str) -> str:
    """
    Get information about a pupil's report PDF for a specific period.

    Note: This tool provides metadata. To download the actual PDF, you'll need
    to access it directly through the ADAM web interface.

    Args:
        period_id: The reporting period ID
        pupil_id: The pupil's ID or admission number

    Returns:
        Information about report availability
    """
    try:
        # Note: The actual PDF endpoint returns binary data, which can't be displayed in text
        # This tool acknowledges the endpoint exists but directs users to the web interface
        return (
            f"Report PDF for pupil {pupil_id} in period {period_id}:\n"
            f"To download the PDF report, please access:\n"
            f"ADAM Web Interface → Reports → Select Period {period_id}\n\n"
            f"Note: PDF downloads are not supported through this text interface."
        )
    except AdamAPIError as e:
        return f"Error retrieving report information: {e.message}"


# ============================================================================
# BEHAVIOR AND RECORDS TOOLS
# ============================================================================


@mcp.tool()
async def get_recent_pupil_records(pupil_id: str) -> str:
    """
    Get recent behavior and achievement records for a pupil.

    This includes both positive records (achievements, awards, commendations)
    and negative records (disciplinary actions, demerits).

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Formatted string with recent records
    """
    try:
        result = await api_client.get_recent_pupil_records(pupil_id)
        return f"Recent Pupil Records:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving pupil records: {e.message}"


@mcp.tool()
async def get_pupil_records_by_date(
    pupil_id: str, start_date: str = None, end_date: str = None
) -> str:
    """
    Get all behavior and achievement records for a pupil with optional date filtering.

    Args:
        pupil_id: The pupil's ID or admission number
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)

    Returns:
        Formatted string with pupil records
    """
    try:
        result = await api_client.get_pupil_records_date_range(pupil_id, start_date, end_date)
        date_range = ""
        if start_date and end_date:
            date_range = f" ({start_date} to {end_date})"
        elif start_date:
            date_range = f" (from {start_date})"
        return f"Pupil Records{date_range}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving pupil records: {e.message}"


# ============================================================================
# MEDICAL AND SPORTS TOOLS
# ============================================================================


@mcp.tool()
async def get_off_sport_list(date: str = None) -> str:
    """
    Get the list of pupils who are off sport (cannot participate in physical activities).

    This is useful for PE teachers and sports coordinators to know which pupils
    should not participate in physical activities on a given day.

    Args:
        date: Date in YYYY-MM-DD format (e.g., "2024-03-15"). If not provided, returns today's list.

    Returns:
        Formatted string with list of pupil IDs who are off sport
    """
    try:
        result = await api_client.get_off_sport_list(date)
        date_str = date if date else "today"
        return f"Off-Sport List for {date_str}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving off-sport list: {e.message}"


# ============================================================================
# DIRECTORY AND LOOKUP TOOLS
# ============================================================================


@mcp.tool()
async def get_all_pupil_contacts() -> str:
    """
    Get a complete contact list of all pupils in the school.

    This returns basic contact information for all pupils including names,
    email addresses, phone numbers, and grades.

    Returns:
        Formatted string with all pupil contacts
    """
    try:
        result = await api_client.get_all_pupil_contacts()
        return f"All Pupil Contacts:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving pupil contacts: {e.message}"


@mcp.tool()
async def get_subjects_by_grade(grade: str) -> str:
    """
    Get all subjects available for a specific grade level.

    This shows which subjects are offered for a particular grade, including
    subject names, short codes, and categories (core subjects, electives, etc.).

    Args:
        grade: Grade level (e.g., "8", "9", "10", "11", "12")

    Returns:
        Formatted string with subjects for the grade
    """
    try:
        result = await api_client.get_subjects_by_grade(grade)
        return f"Subjects for Grade {grade}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving subjects: {e.message}"


@mcp.tool()
async def get_family_children(family_id: str) -> str:
    """
    Get all children (pupils) associated with a specific family.

    This shows all pupils linked to a family, including their names, grades,
    admin numbers, and relationship to the family.

    Args:
        family_id: The family ID

    Returns:
        Formatted string with family's children
    """
    try:
        result = await api_client.get_family_children(family_id)
        return f"Children for Family {family_id}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving family children: {e.message}"


@mcp.tool()
async def get_pupil_photo_info(pupil_id: str) -> str:
    """
    Get information about a pupil's photo.

    Note: This tool provides metadata. Pupil photos are binary image files that
    cannot be displayed in this text interface. Access photos through the ADAM
    web interface.

    Args:
        pupil_id: The pupil's ID or admission number

    Returns:
        Information about photo availability
    """
    try:
        # Note: The actual image endpoint returns binary data
        # This tool acknowledges the endpoint exists but directs users to the web interface
        return (
            f"Photo for pupil {pupil_id}:\n"
            f"To view the pupil's photo, please access:\n"
            f"ADAM Web Interface → Pupils → View Profile → Photo\n\n"
            f"Note: Image display is not supported through this text interface."
        )
    except AdamAPIError as e:
        return f"Error retrieving photo information: {e.message}"


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
    import signal
    import sys

    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        print("\n\nShutting down gracefully...")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

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
    # Signal handlers above ensure graceful shutdown and port release
    try:
        mcp.run(
            transport="http",
            host=Config.MCP_HOST,
            port=Config.MCP_PORT
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
