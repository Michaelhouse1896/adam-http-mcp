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

    async def get_pupil_classes(self, pupil_id: str) -> dict[str, Any]:
        """
        Get list of classes for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing the pupil's class list with teacher information
        """
        return await self._make_request("classes", "pupilteachers", [pupil_id])

    async def get_pupil_academic_records(self, pupil_id: str) -> dict[str, Any]:
        """
        Get academic records for a pupil across all reporting periods.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing academic records/marks by subject and period
        """
        return await self._make_request("reporting", "subjectmarksbypupil", [pupil_id])

    # Teacher and Contact Methods

    async def get_pupil_teachers(self, pupil_id: str) -> dict[str, Any]:
        """
        Get list of teachers for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing teacher information including names and email addresses
        """
        return await self._make_request("classes", "pupilteachers", [pupil_id])

    async def get_pupil_family_relationships(self, pupil_id: str) -> dict[str, Any]:
        """
        Get family relationships for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing family relationships including family IDs
        """
        return await self._make_request("familyrelationships", "pupil", [pupil_id])

    async def get_family_emails(self, family_id: str) -> dict[str, Any]:
        """
        Get email addresses for a family.

        Args:
            family_id: The family ID

        Returns:
            Dictionary containing family email addresses
        """
        return await self._make_request("families", "email", [family_id])

    async def get_all_family_contacts(self) -> dict[str, Any]:
        """
        Get contact list of all families.

        Returns:
            Dictionary containing contact information for all families
        """
        return await self._make_request("families", "contactlist")

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

    # Assessment and Reporting Methods

    async def get_recent_assessment_results(self, pupil_id: str) -> dict[str, Any]:
        """
        Get recent assessment results for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing recent assessment results with marks and comments
        """
        return await self._make_request("assessment", "recentresults", [pupil_id])

    async def get_pupil_markbook(self, period_id: str, pupil_id: str) -> dict[str, Any]:
        """
        Get detailed markbook/assessment data for a pupil in a reporting period.

        Args:
            period_id: The reporting period ID
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing detailed assessment breakdown by subject and category
        """
        return await self._make_request("reporting", "markbook", [period_id, pupil_id])

    async def get_reporting_periods(self, year: str = None) -> dict[str, Any]:
        """
        Get all reporting periods for a specific year.

        Args:
            year: Year (optional, defaults to current year on server)

        Returns:
            Dictionary containing reporting periods with dates
        """
        if year:
            return await self._make_request("reporting", "periods", [year])
        else:
            return await self._make_request("reporting", "periods")

    async def get_pupil_reporting_periods(self, pupil_id: str) -> dict[str, Any]:
        """
        Get reporting periods available for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing available reporting periods for the pupil
        """
        return await self._make_request("reporting", "pupilreportingperiods", [pupil_id])

    async def get_pupil_report_pdf(self, period_id: str, pupil_id: str) -> bytes:
        """
        Get a pupil's report document (PDF).

        Args:
            period_id: The reporting period ID
            pupil_id: The pupil's ID or admission number

        Returns:
            Binary PDF data
        """
        # This returns binary PDF data, not JSON
        result = await self._make_request("reporting", "report", [period_id, pupil_id])
        return result

    # Records and Behavior Methods

    async def get_recent_pupil_records(self, pupil_id: str) -> dict[str, Any]:
        """
        Get recent records (achievements/disciplinary) for a pupil.

        Args:
            pupil_id: The pupil's ID or admission number

        Returns:
            Dictionary containing recent behavior and achievement records
        """
        return await self._make_request("recordsandpoints", "recentpupilrecords", [pupil_id])

    async def get_pupil_records_date_range(
        self, pupil_id: str, start_date: str = None, end_date: str = None
    ) -> dict[str, Any]:
        """
        Get all records for a pupil with optional date range filtering.

        Args:
            pupil_id: The pupil's ID or admission number
            start_date: Start date (format: YYYY-MM-DD, optional)
            end_date: End date (format: YYYY-MM-DD, optional)

        Returns:
            Dictionary containing behavior and achievement records
        """
        params = [pupil_id]
        if start_date:
            params.append(start_date)
            if end_date:
                params.append(end_date)
        return await self._make_request("recordsandpoints", "pupilrecords", params)

    # Medical and Sports Methods

    async def get_off_sport_list(self, date: str = None) -> dict[str, Any]:
        """
        Get the off-sport list for a specific date.

        Args:
            date: Date in YYYY-MM-DD format (optional, defaults to today)

        Returns:
            Dictionary containing list of pupil IDs who are off sport
        """
        if date:
            return await self._make_request("medical", "offsport", [date])
        else:
            return await self._make_request("medical", "offsport")

    # Directory and Lookup Methods

    async def get_all_pupil_contacts(self) -> dict[str, Any]:
        """
        Get contact list of all pupils.

        Returns:
            Dictionary containing contact information for all pupils
        """
        return await self._make_request("pupils", "contactlist")

    async def get_subjects_by_grade(self, grade: str) -> dict[str, Any]:
        """
        Get subjects for a specific grade.

        Args:
            grade: Grade level (e.g., "10")

        Returns:
            Dictionary containing subjects available for the grade
        """
        return await self._make_request("subjects", "get_by_grade", [grade])

    async def get_family_children(self, family_id: str) -> dict[str, Any]:
        """
        Get children associated with a family.

        Args:
            family_id: The family ID

        Returns:
            Dictionary containing pupils linked to the family
        """
        return await self._make_request("families", "children", [family_id])

    async def get_pupil_image(self, pupil_id: str, width: int = 200) -> bytes:
        """
        Get a pupil's photo/image.

        Args:
            pupil_id: The pupil's ID or admission number
            width: Image width in pixels (default: 200)

        Returns:
            Binary image data
        """
        return await self._make_request("pupils", "image", [pupil_id, str(width)])

    # Data Query API Methods (for name-based lookups)

    async def get_all_pupils_data(self) -> dict[str, Any]:
        """
        Get all current pupils data from Data Query API.

        Returns:
            Dictionary containing all pupil records with detailed information

        Raises:
            AdamAPIError: If the secret is not configured or API returns an error
        """
        if not Config.ADAM_DATAQUERY_PUPILS_SECRET:
            raise AdamAPIError("ADAM_DATAQUERY_PUPILS_SECRET not configured")
        return await self._make_request("dataquery", "get", [Config.ADAM_DATAQUERY_PUPILS_SECRET])

    async def get_all_families_data(self) -> dict[str, Any]:
        """
        Get all current families data from Data Query API.

        Returns:
            Dictionary containing all family records with detailed information

        Raises:
            AdamAPIError: If the secret is not configured or API returns an error
        """
        if not Config.ADAM_DATAQUERY_FAMILIES_SECRET:
            raise AdamAPIError("ADAM_DATAQUERY_FAMILIES_SECRET not configured")
        return await self._make_request("dataquery", "get", [Config.ADAM_DATAQUERY_FAMILIES_SECRET])

    async def get_all_staff_data(self) -> dict[str, Any]:
        """
        Get all current staff data from Data Query API.

        Returns:
            Dictionary containing all staff records with detailed information

        Raises:
            AdamAPIError: If the secret is not configured or API returns an error
        """
        if not Config.ADAM_DATAQUERY_STAFF_SECRET:
            raise AdamAPIError("ADAM_DATAQUERY_STAFF_SECRET not configured")
        return await self._make_request("dataquery", "get", [Config.ADAM_DATAQUERY_STAFF_SECRET])

    async def find_pupils_by_name(self, name: str) -> list[dict[str, Any]]:
        """
        Find pupils by name (searches first name, last name, and preferred name).

        Args:
            name: Name to search for (case-insensitive, partial match)

        Returns:
            List of matching pupil records with ID, name, grade, and admin number
        """
        data = await self.get_all_pupils_data()
        search_term = name.lower().strip()
        results = []

        for record in data.values():
            last_name = record.get("last_name_2", "").lower()
            preferred_name = record.get("preferred_name_3", "").lower()
            full_first_names = record.get("full_first_names_4", "").lower()

            # Match if search term appears in any name field
            if (search_term in last_name or
                search_term in preferred_name or
                search_term in full_first_names or
                search_term in f"{preferred_name} {last_name}" or
                search_term in f"{full_first_names} {last_name}"):
                results.append({
                    "pupil_id": record.get("adam_id_257"),
                    "admin_number": record.get("admin_number_1"),
                    "last_name": record.get("last_name_2"),
                    "preferred_name": record.get("preferred_name_3"),
                    "full_first_names": record.get("full_first_names_4"),
                    "grade": record.get("grade_9"),
                    "email": record.get("email_21"),
                })

        return results

    async def find_families_by_name(self, name: str) -> list[dict[str, Any]]:
        """
        Find families by name (searches family surname and parent names).

        Args:
            name: Name to search for (case-insensitive, partial match)

        Returns:
            List of matching family records with ID and names
        """
        data = await self.get_all_families_data()
        search_term = name.lower().strip()
        results = []

        for record in data.values():
            family_surname = record.get("family_greeting_surname_133", "").lower()
            family_first_names = record.get("family_greeting_first_names_143", "").lower()
            address_name = record.get("family_address_name_132", "").lower()

            # Match if search term appears in any family name field
            if (search_term in family_surname or
                search_term in family_first_names or
                search_term in address_name or
                search_term in f"{family_first_names} {family_surname}"):
                results.append({
                    "family_id": record.get("family_identifier_253"),
                    "family_surname": record.get("family_greeting_surname_133"),
                    "family_first_names": record.get("family_greeting_first_names_143"),
                    "address_name": record.get("family_address_name_132"),
                    "father_greeting": record.get("father_039_s_greeting_288"),
                    "mother_greeting": record.get("mother_039_s_greeting_289"),
                })

        return results

    async def find_staff_by_name(self, name: str) -> list[dict[str, Any]]:
        """
        Find staff by name (searches first name, last name, and preferred name).

        Args:
            name: Name to search for (case-insensitive, partial match)

        Returns:
            List of matching staff records with ID, name, and position
        """
        data = await self.get_all_staff_data()
        search_term = name.lower().strip()
        results = []

        for record in data.values():
            last_name = record.get("last_name_31", "").lower()
            preferred_name = record.get("first_name_preferred_32", "").lower()
            full_name = record.get("full_first_name_142", "").lower()

            # Match if search term appears in any name field
            if (search_term in last_name or
                search_term in preferred_name or
                search_term in full_name or
                search_term in f"{preferred_name} {last_name}"):
                results.append({
                    "staff_id": record.get("adam_identifier_284"),
                    "admin_no": record.get("admin_no_30"),
                    "last_name": record.get("last_name_31"),
                    "preferred_name": record.get("first_name_preferred_32"),
                    "full_name": record.get("full_first_name_142"),
                    "position": record.get("position_233"),
                    "department": record.get("department_49"),
                    "email": record.get("email_address_67"),
                })

        return results
