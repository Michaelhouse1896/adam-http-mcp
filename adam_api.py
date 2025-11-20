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

    # Class and Registration Methods

    async def get_grade_registrations(self, grade: str) -> dict[str, Any]:
        """
        Get all class registrations for a specific grade.

        Args:
            grade: Grade level (e.g., "8", "9", "10", "11", "12")

        Returns:
            Dictionary containing registration records with pupil, class, and teacher information
        """
        return await self._make_request("registrations", "grade", [grade])

    async def get_pupil_family_relationships(self, pupil_id: str) -> dict[str, Any]:
        """
        Get family relationships for a specific pupil.

        Args:
            pupil_id: The pupil's ID

        Returns:
            Dictionary containing family relationship information including family_id
        """
        return await self._make_request("familyrelationships", "pupil", [pupil_id])

    async def get_class_parent_emails(
        self, grade: str, class_description: str
    ) -> dict[str, Any]:
        """
        Get all parent email addresses for pupils in a specific class.

        This orchestrates multiple API calls to:
        1. Get all registrations for the grade
        2. Filter by class description
        3. Get family relationships for each pupil
        4. Get email addresses for each family
        5. Deduplicate and format results

        Args:
            grade: Grade level (e.g., "8", "9", "10", "11", "12")
            class_description: Class description to search for (case-insensitive, partial match)
                             Examples: "Mathematics", "10A", "English"

        Returns:
            Dictionary containing:
            - pupils: List of pupils with their families and emails
            - all_emails: Deduplicated list of all email addresses
            - summary: Statistics about the class
        """
        # Get all registrations for the grade
        registrations_response = await self.get_grade_registrations(grade)

        # Handle response - could be a list or dict with 'data' key
        if isinstance(registrations_response, dict):
            registrations_data = registrations_response.get("data", registrations_response)
        else:
            registrations_data = registrations_response

        # Ensure we have a list
        if not isinstance(registrations_data, list):
            raise AdamAPIError(f"Unexpected registrations data format: {type(registrations_data)}")

        # Filter registrations by class description (case-insensitive partial match)
        search_term = class_description.lower().strip()
        matching_registrations = []
        seen_pupils = set()

        # Debug: log first few class descriptions to help troubleshoot
        if registrations_data:
            sample_classes = set()
            for reg in registrations_data[:10]:
                sample_classes.add(reg.get("class_description", "N/A"))
            print(f"DEBUG: Sample class descriptions: {list(sample_classes)[:5]}")
            print(f"DEBUG: Search term: '{search_term}'")
            print(f"DEBUG: Total registrations: {len(registrations_data)}")

        for reg in registrations_data:
            class_desc = reg.get("class_description", "").lower()
            pupil_id = reg.get("pupil_id")

            # Match class description and avoid duplicate pupils
            if search_term in class_desc and pupil_id not in seen_pupils:
                matching_registrations.append(reg)
                seen_pupils.add(pupil_id)

        print(f"DEBUG: Found {len(matching_registrations)} matching registrations")

        if not matching_registrations:
            return {
                "pupils": [],
                "all_emails": [],
                "summary": {
                    "total_pupils": 0,
                    "total_families": 0,
                    "total_emails": 0,
                    "class_description": class_description,
                    "grade": grade,
                },
            }

        # Collect pupil and family data
        pupils_data = []
        all_emails_set = set()

        for reg in matching_registrations:
            pupil_id = reg.get("pupil_id")
            pupil_info = {
                "pupil_id": pupil_id,
                "pupil_firstname": reg.get("pupil_firstname"),
                "pupil_lastname": reg.get("pupil_lastname"),
                "pupil_admin": reg.get("pupil_admin"),
                "class_description": reg.get("class_description"),
                "families": [],
            }

            # Get family relationships for this pupil
            try:
                family_rels_response = await self.get_pupil_family_relationships(str(pupil_id))

                # Handle response - could be a list or dict with 'data' key
                if isinstance(family_rels_response, dict):
                    family_rels = family_rels_response.get("data", family_rels_response)
                else:
                    family_rels = family_rels_response

                # Ensure we have a list
                if not isinstance(family_rels, list):
                    # Skip this pupil if we can't get proper family data
                    continue

                # Get emails for each family
                for family_rel in family_rels:
                    family_id = family_rel.get("family_id")
                    if not family_id:
                        continue

                    try:
                        # Get all email addresses for this family
                        emails_data = await self.get_family_emails(str(family_id))
                        emails = emails_data if isinstance(emails_data, list) else []

                        # Add to pupil's family list
                        pupil_info["families"].append({
                            "family_id": family_id,
                            "relationship": family_rel.get("relationship"),
                            "family_name": f"{family_rel.get('family_primary_firstname', '')} {family_rel.get('family_primary_lastname', '')}".strip(),
                            "emails": emails,
                        })

                        # Add emails to global set (deduplicate)
                        for email in emails:
                            if email:  # Skip empty emails
                                all_emails_set.add(email.strip())

                    except AdamAPIError:
                        # Skip families with email retrieval errors
                        continue

            except AdamAPIError:
                # Skip pupils with family relationship errors
                continue

            pupils_data.append(pupil_info)

        # Generate summary
        total_families = sum(len(p["families"]) for p in pupils_data)
        summary = {
            "total_pupils": len(pupils_data),
            "total_families": total_families,
            "total_emails": len(all_emails_set),
            "class_description": class_description,
            "grade": grade,
            "matched_class_names": list(set(r.get("class_description") for r in matching_registrations)),
        }

        return {
            "pupils": pupils_data,
            "all_emails": sorted(list(all_emails_set)),  # Sort for consistency
            "summary": summary,
        }
