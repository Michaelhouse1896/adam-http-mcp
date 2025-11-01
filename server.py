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
