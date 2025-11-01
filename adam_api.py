"""ADAM API client wrapper for MCP server."""

import httpx
from typing import Any, Optional
from urllib.parse import quote
from config import Config


class AdamAPIError(Exception):
    """Custom exception for ADAM API errors."""

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AdamAPIClient:
    """Client for interacting with ADAM School MIS API."""

    def __init__(self):
        """Initialize the ADAM API client."""
        self.base_url = Config.ADAM_BASE_URL
        self.headers = Config.get_auth_header()
        self.headers["Content-Type"] = "application/json"
        self.timeout = 30.0
        self.verify_ssl = Config.ADAM_VERIFY_SSL

    def _encode_param(self, param: str) -> str:
        """Percent encode a parameter value."""
        return quote(str(param), safe="")

    async def _make_request(
        self, module: str, resource: str, params: Optional[list[str]] = None, method: str = "GET"
    ) -> dict[str, Any]:
        """
        Make a request to the ADAM API.

        Args:
            module: The API module (e.g., "Pupils", "Families")
            resource: The resource endpoint (e.g., "pupil", "email")
            params: List of parameters to append to URL
            method: HTTP method (GET or POST)

        Returns:
            Parsed JSON response data

        Raises:
            AdamAPIError: If the API returns an error
        """
        # Build URL
        url_parts = [self.base_url, module, resource]
        if params:
            encoded_params = [self._encode_param(p) for p in params]
            url_parts.extend(encoded_params)

        url = "/".join(url_parts)

        try:
            async with httpx.AsyncClient(timeout=self.timeout, verify=self.verify_ssl) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                json_data = response.json()

                # Check ADAM API response format
                if "response" in json_data:
                    if json_data["response"]["code"] != 200:
                        error_msg = json_data["response"].get("error", "Unknown error")
                        raise AdamAPIError(error_msg, json_data["response"]["code"])

                return json_data.get("data", json_data)

        except httpx.HTTPStatusError as e:
            raise AdamAPIError(f"HTTP error: {e.response.status_code}", e.response.status_code)
        except httpx.RequestError as e:
            raise AdamAPIError(f"Request error: {str(e)}")
        except Exception as e:
            raise AdamAPIError(f"Unexpected error: {str(e)}")

    # Pupil Information Methods

    async def get_pupil_info(self, pupil_id: str) -> dict[str, Any]:
        """
        Get detailed information about a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing pupil information including:
            - Basic info (name, grade, etc.)
            - Boarding house
            - Medical aid information
        """
        return await self._make_request("pupils", "pupil", [pupil_id])

    async def search_pupils(self, search_term: str) -> dict[str, Any]:
        """
        Search for pupils by name or other identifying information.

        Args:
            search_term: Name or search term to find pupils

        Returns:
            Dictionary containing list of matching pupils with their IDs and basic info
        """
        # ADAM API typically uses a search endpoint
        # This might need adjustment based on your ADAM API version
        return await self._make_request("pupils", "search", [search_term])

    async def get_pupil_classes(self, pupil_id: str) -> dict[str, Any]:
        """
        Get list of classes for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing the pupil's class list
        """
        # This might need to be adjusted based on actual ADAM API endpoint
        # Using a common endpoint structure
        return await self._make_request("pupils", "classes", [pupil_id])

    async def get_pupil_academic_records(
        self, pupil_id: str, subject: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Get academic records for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number
            subject: Optional subject filter (e.g., "Biology", "Mathematics")

        Returns:
            Dictionary containing academic records/marks
        """
        params = [pupil_id]
        if subject:
            params.append(subject)

        return await self._make_request("reporting", "results", params)

    async def get_report_comments(self, pupil_id: str, term: Optional[str] = None) -> dict[str, Any]:
        """
        Get report card comments summary for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number
            term: Optional term filter (e.g., "Term 1", "2024")

        Returns:
            Dictionary containing report comments
        """
        params = [pupil_id]
        if term:
            params.append(term)

        return await self._make_request("reporting", "comments", params)

    # Teacher and Contact Methods

    async def get_pupil_teachers(self, pupil_id: str) -> dict[str, Any]:
        """
        Get list of teachers for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing teacher information including names and email addresses
        """
        return await self._make_request("pupils", "teachers", [pupil_id])

    async def get_family_emails(self, family_id: str) -> dict[str, Any]:
        """
        Get email addresses for a family.

        Args:
            family_id: The family ID

        Returns:
            Dictionary containing family email addresses
        """
        return await self._make_request("families", "email", [family_id])

    async def get_class_parent_emails(self, class_id: str) -> dict[str, Any]:
        """
        Get parent email addresses for all pupils in a class.

        Args:
            class_id: The class ID or name

        Returns:
            Dictionary containing parent email addresses for the class
        """
        return await self._make_request("classes", "parents", [class_id])

    # Utility Methods

    async def test_connection(self) -> dict[str, Any]:
        """
        Test the API connection.

        Returns:
            Dictionary with test results
        """
        try:
            result = await self._make_request("request", "test")
            return {"success": True, "message": "Connection successful", "data": result}
        except AdamAPIError as e:
            return {"success": False, "message": str(e), "status_code": e.status_code}

    async def get_absence_summary(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """
        Get absence summary for a date range.

        Args:
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)

        Returns:
            Dictionary containing absence counts
        """
        return await self._make_request("absentees", "summarycount", [start_date, end_date])

    async def get_absence_list(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """
        Get detailed absence records for a date range.

        Args:
            start_date: Start date (format: YYYY-MM-DD)
            end_date: End date (format: YYYY-MM-DD)

        Returns:
            Dictionary containing detailed absence records
        """
        return await self._make_request("absentees", "list", [start_date, end_date])
