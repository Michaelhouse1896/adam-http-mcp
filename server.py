"""ADAM MCP Server - Model Context Protocol server for ADAM School MIS."""

from typing import Optional
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
async def search_pupils(name: str) -> str:
    """
    Search for pupils by name.

    Use this tool when you need to find a pupil's ID or when you only know
    the pupil's name. This returns a list of matching pupils with their IDs
    and basic information.

    Args:
        name: The pupil's name or part of their name to search for

    Returns:
        Formatted string with list of matching pupils and their IDs
    """
    try:
        result = await api_client.search_pupils(name)
        return f"Search Results for '{name}':\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error searching for pupils: {e.message}"


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
async def get_pupil_academic_record(pupil_id: str, subject: Optional[str] = None) -> str:
    """
    Get academic records and marks for a pupil.

    This retrieves the pupil's marks, grades, and assessment results.
    Optionally filter by a specific subject.

    Args:
        pupil_id: The pupil's ID or admission number
        subject: Optional subject name to filter results (e.g., "Biology", "Mathematics")

    Returns:
        Formatted string with academic records
    """
    try:
        result = await api_client.get_pupil_academic_records(pupil_id, subject)
        subject_info = f" for {subject}" if subject else ""
        return f"Academic Records{subject_info}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving academic records: {e.message}"


@mcp.tool()
async def get_report_card_summary(pupil_id: str, term: Optional[str] = None) -> str:
    """
    Get report card comments and summary for a pupil.

    This retrieves comments from teachers on the pupil's report cards.
    Optionally filter by a specific term.

    Args:
        pupil_id: The pupil's ID or admission number
        term: Optional term filter (e.g., "Term 1", "2024")

    Returns:
        Formatted string with report comments
    """
    try:
        result = await api_client.get_report_comments(pupil_id, term)
        term_info = f" for {term}" if term else ""
        return f"Report Card Comments{term_info}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving report comments: {e.message}"


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
async def get_class_parent_emails(class_id: str) -> str:
    """
    Get parent email addresses for all pupils in a specific class.

    This is useful for sending class-wide communications to parents.

    Args:
        class_id: The class ID or class name

    Returns:
        Formatted string with parent email addresses
    """
    try:
        result = await api_client.get_class_parent_emails(class_id)
        return f"Parent Email Addresses for Class {class_id}:\n{_format_json(result)}"
    except AdamAPIError as e:
        return f"Error retrieving parent emails: {e.message}"


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
