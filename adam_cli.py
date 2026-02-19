#!/usr/bin/env python3
"""ADAM CLI - Command-line interface for ADAM School Management Information System."""

import argparse
import asyncio
import csv
import io
import json
import os
import signal
import sys
from typing import Any, Optional
from urllib.parse import quote

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class Config:
    """Configuration loaded from environment / .env file."""

    ADAM_API_TOKEN: str = os.getenv("ADAM_API_TOKEN", "")
    ADAM_BASE_URL: str = os.getenv("ADAM_BASE_URL", "")
    ADAM_VERIFY_SSL: bool = os.getenv("ADAM_VERIFY_SSL", "true").lower() in (
        "true",
        "1",
        "yes",
    )
    ADAM_DATAQUERY_PUPILS_SECRET: str = os.getenv("ADAM_DATAQUERY_PUPILS_SECRET", "")
    ADAM_DATAQUERY_FAMILIES_SECRET: str = os.getenv(
        "ADAM_DATAQUERY_FAMILIES_SECRET", ""
    )
    ADAM_DATAQUERY_STAFF_SECRET: str = os.getenv("ADAM_DATAQUERY_STAFF_SECRET", "")

    @classmethod
    def validate(cls) -> None:
        errors: list[str] = []
        if not cls.ADAM_API_TOKEN:
            errors.append("ADAM_API_TOKEN is not set")
        elif len(cls.ADAM_API_TOKEN) != 30:
            errors.append("ADAM_API_TOKEN must be exactly 30 characters")
        if not cls.ADAM_BASE_URL:
            errors.append("ADAM_BASE_URL is not set")
        elif not cls.ADAM_BASE_URL.startswith(("http://", "https://")):
            errors.append("ADAM_BASE_URL must start with http:// or https://")
        if errors:
            raise SystemExit(
                "Configuration error:\n  "
                + "\n  ".join(errors)
                + "\nEnsure ADAM_API_TOKEN and ADAM_BASE_URL environment variables are set."
            )

    @classmethod
    def get_auth_header(cls) -> dict[str, str]:
        return {"Authorization": f"Bearer {cls.ADAM_API_TOKEN}"}


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------


class AdamAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AdamAPIClient:
    def __init__(self) -> None:
        self.base_url = Config.ADAM_BASE_URL
        self.headers = {**Config.get_auth_header(), "Content-Type": "application/json"}
        self.timeout = 30.0
        self.verify_ssl = Config.ADAM_VERIFY_SSL

    @staticmethod
    def _encode_param(param: str) -> str:
        return quote(str(param), safe="")

    async def _make_request(
        self,
        module: str,
        resource: str,
        params: Optional[list[str]] = None,
        method: str = "GET",
    ) -> dict[str, Any]:
        url_parts = [self.base_url, module, resource]
        if params:
            url_parts.extend(self._encode_param(p) for p in params)
        url = "/".join(url_parts)

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, verify=self.verify_ssl
            ) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                json_data = response.json()

                if "response" in json_data:
                    if json_data["response"]["code"] != 200:
                        error_msg = json_data["response"].get("error", "Unknown error")
                        raise AdamAPIError(error_msg, json_data["response"]["code"])

                return json_data.get("data", json_data)

        except httpx.HTTPStatusError as e:
            raise AdamAPIError(
                f"HTTP error: {e.response.status_code}", e.response.status_code
            )
        except httpx.RequestError as e:
            raise AdamAPIError(f"Request error: {str(e)}")
        except AdamAPIError:
            raise
        except Exception as e:
            raise AdamAPIError(f"Unexpected error: {str(e)}")

    # -- Test -----------------------------------------------------------------

    async def test_connection(self) -> dict[str, Any]:
        try:
            result = await self._make_request("request", "test")
            return {"success": True, "message": "Connection successful", "data": result}
        except AdamAPIError as e:
            return {"success": False, "message": str(e), "status_code": e.status_code}

    # -- Pupils ---------------------------------------------------------------

    async def get_pupil_info(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request("pupils", "pupil", [pupil_id])

    async def get_pupil_classes(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request("classes", "pupilteachers", [pupil_id])

    async def get_all_pupil_contacts(self) -> dict[str, Any]:
        return await self._make_request("pupils", "contactlist")

    async def search_pupil_by_id_number(self, id_number: str) -> dict[str, Any]:
        return await self._make_request("pupils", "searchbyid", [id_number])

    async def get_pupil_fields(self, action: str | None = None) -> dict[str, Any]:
        if action:
            return await self._make_request("pupils", "fields", [action])
        return await self._make_request("pupils", "fields")

    async def search_pupil_admin(self, search_term: str) -> dict[str, Any]:
        return await self._make_request("pupils", "search-admin", [search_term])

    # -- Calendar -------------------------------------------------------------

    async def get_calendar_pupil_links(self) -> dict[str, Any]:
        return await self._make_request("calendar", "pupillinks")

    async def get_calendar_staff_links(self) -> dict[str, Any]:
        return await self._make_request("calendar", "stafflinks")

    # -- Academics ------------------------------------------------------------

    async def get_pupil_academic_records(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request("reporting", "subjectmarksbypupil", [pupil_id])

    async def get_recent_assessment_results(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request("assessment", "recentresults", [pupil_id])

    async def get_pupil_markbook(
        self, period_id: str, pupil_id: str
    ) -> dict[str, Any]:
        return await self._make_request("reporting", "markbook", [period_id, pupil_id])

    async def get_reporting_periods(self, year: str | None = None) -> dict[str, Any]:
        if year:
            return await self._make_request("reporting", "periods", [year])
        return await self._make_request("reporting", "periods")

    async def get_pupil_reporting_periods(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request(
            "reporting", "pupilreportingperiods", [pupil_id]
        )

    async def get_reporting_results(self, period_id: str) -> dict[str, Any]:
        return await self._make_request("reporting", "results", [period_id])

    async def get_previous_reports(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request("reporting", "previousreports", [pupil_id])

    async def get_question_breakdown(self, assessment_id: str) -> dict[str, Any]:
        return await self._make_request(
            "questions", "questionbreakdown", [assessment_id]
        )

    # -- Teachers -------------------------------------------------------------

    async def get_pupil_teachers(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request("classes", "pupilteachers", [pupil_id])

    # -- Families -------------------------------------------------------------

    async def get_pupil_family_relationships(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request("familyrelationships", "pupil", [pupil_id])

    async def get_family_emails(self, family_id: str) -> dict[str, Any]:
        return await self._make_request("families", "email", [family_id])

    async def get_all_family_contacts(self) -> dict[str, Any]:
        return await self._make_request("families", "contactlist")

    async def get_family_children(self, family_id: str) -> dict[str, Any]:
        return await self._make_request("families", "children", [family_id])

    async def get_family_current_children(self, family_id: str) -> dict[str, Any]:
        return await self._make_request("families", "currentchildren", [family_id])

    async def search_family_by_id_number(self, id_number: str) -> dict[str, Any]:
        return await self._make_request("families", "searchbyid", [id_number])

    async def get_family_relationship_types(self) -> dict[str, Any]:
        return await self._make_request("families", "familyrelationships")

    async def get_family_relationships(self, family_id: str) -> dict[str, Any]:
        return await self._make_request("familyrelationships", "family", [family_id])

    async def get_family_login_privileges(self, family_id: str) -> dict[str, Any]:
        return await self._make_request("familylogin", "privileges", [family_id])

    # -- Classes --------------------------------------------------------------

    async def get_grade_registrations(self, grade: str) -> dict[str, Any]:
        return await self._make_request("registrations", "grade", [grade])

    async def get_classes_by_grade_period_subject(
        self, grade: str, period_id: str, subject_id: str
    ) -> dict[str, Any]:
        return await self._make_request(
            "classes", "bygradeperiodsubject", [grade, period_id, subject_id]
        )

    async def get_class_parent_emails(
        self, grade: str, class_description: str
    ) -> dict[str, Any]:
        registrations_response = await self.get_grade_registrations(grade)

        if isinstance(registrations_response, dict):
            registrations_data = registrations_response.get(
                "data", registrations_response
            )
        else:
            registrations_data = registrations_response

        if not isinstance(registrations_data, list):
            raise AdamAPIError(
                f"Unexpected registrations data format: {type(registrations_data)}"
            )

        search_term = class_description.lower().strip()
        matching_registrations: list[dict] = []
        seen_pupils: set = set()

        for reg in registrations_data:
            class_desc = reg.get("class_description", "").lower()
            pupil_id = reg.get("pupil_id")
            if search_term in class_desc and pupil_id not in seen_pupils:
                matching_registrations.append(reg)
                seen_pupils.add(pupil_id)

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

        pupils_data: list[dict] = []
        all_emails_set: set[str] = set()

        for reg in matching_registrations:
            pupil_id = reg.get("pupil_id")
            pupil_info: dict[str, Any] = {
                "pupil_id": pupil_id,
                "pupil_firstname": reg.get("pupil_firstname"),
                "pupil_lastname": reg.get("pupil_lastname"),
                "pupil_admin": reg.get("pupil_admin"),
                "class_description": reg.get("class_description"),
                "families": [],
            }

            try:
                family_rels_response = (
                    await self.get_pupil_family_relationships(str(pupil_id))
                )
                if isinstance(family_rels_response, dict):
                    family_rels = family_rels_response.get(
                        "data", family_rels_response
                    )
                else:
                    family_rels = family_rels_response

                if not isinstance(family_rels, list):
                    continue

                for family_rel in family_rels:
                    family_id = family_rel.get("family_id")
                    if not family_id:
                        continue
                    try:
                        emails_data = await self.get_family_emails(str(family_id))
                        emails = emails_data if isinstance(emails_data, list) else []
                        pupil_info["families"].append(
                            {
                                "family_id": family_id,
                                "relationship": family_rel.get("relationship"),
                                "family_name": f"{family_rel.get('family_primary_firstname', '')} {family_rel.get('family_primary_lastname', '')}".strip(),
                                "emails": emails,
                            }
                        )
                        for email in emails:
                            if email:
                                all_emails_set.add(email.strip())
                    except AdamAPIError:
                        continue
            except AdamAPIError:
                continue

            pupils_data.append(pupil_info)

        total_families = sum(len(p["families"]) for p in pupils_data)
        return {
            "pupils": pupils_data,
            "all_emails": sorted(all_emails_set),
            "summary": {
                "total_pupils": len(pupils_data),
                "total_families": total_families,
                "total_emails": len(all_emails_set),
                "class_description": class_description,
                "grade": grade,
                "matched_class_names": list(
                    {r.get("class_description") for r in matching_registrations}
                ),
            },
        }

    # -- Attendance -----------------------------------------------------------

    async def get_absence_summary(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        return await self._make_request(
            "absentees", "summarycount", [start_date, end_date]
        )

    async def get_absence_list(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        return await self._make_request("absentees", "list", [start_date, end_date])

    async def get_pupil_days_absent(
        self, pupil_id: str, year: str | None = None
    ) -> dict[str, Any]:
        params = [pupil_id]
        if year:
            params.append(year)
        return await self._make_request("absentees", "daysabsentforpupil", params)

    # -- Leaves ---------------------------------------------------------------

    async def get_approved_leaves(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> dict[str, Any]:
        params: list[str] = []
        if start_date:
            params.append(start_date)
            if end_date:
                params.append(end_date)
        return await self._make_request("leaves", "approved", params or None)

    # -- Records --------------------------------------------------------------

    async def get_recent_pupil_records(self, pupil_id: str) -> dict[str, Any]:
        return await self._make_request(
            "recordsandpoints", "recentpupilrecords", [pupil_id]
        )

    async def get_pupil_records_date_range(
        self,
        pupil_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        params = [pupil_id]
        if start_date:
            params.append(start_date)
            if end_date:
                params.append(end_date)
        return await self._make_request("recordsandpoints", "pupilrecords", params)

    # -- Medical --------------------------------------------------------------

    async def get_off_sport_list(self, date: str | None = None) -> dict[str, Any]:
        if date:
            return await self._make_request("medical", "offsport", [date])
        return await self._make_request("medical", "offsport")

    # -- Subjects -------------------------------------------------------------

    async def get_subjects_by_grade(self, grade: str) -> dict[str, Any]:
        return await self._make_request("subjects", "get_by_grade", [grade])

    async def get_subjects_by_grades(self, grades: str) -> dict[str, Any]:
        return await self._make_request("subjects", "get_by_grades", [grades])

    # -- Psychometric ---------------------------------------------------------

    async def get_psychometric_assessments(
        self, pupil_id: str | None = None, category_id: str | None = None
    ) -> dict[str, Any]:
        params: list[str] = []
        if pupil_id:
            params.append(pupil_id)
            if category_id:
                params.append(category_id)
        return await self._make_request(
            "psychometric", "assessmentsbycategory", params or None
        )

    # -- Messages -------------------------------------------------------------

    async def get_messages(
        self, start_date: str | None = None, end_date: str | None = None
    ) -> dict[str, Any]:
        params: list[str] = []
        if start_date:
            params.append(start_date)
            if end_date:
                params.append(end_date)
        return await self._make_request("messaginglogs", "messages", params or None)

    async def get_message(self, message_id: str) -> dict[str, Any]:
        return await self._make_request("messaginglogs", "message", [message_id])

    # -- Admissions -----------------------------------------------------------

    async def get_registration_status_list(self) -> dict[str, Any]:
        return await self._make_request("registration", "statuslist")

    async def get_registration_statuses(self) -> dict[str, Any]:
        return await self._make_request("registration", "statuses")

    # -- Data Query -----------------------------------------------------------

    async def dataquery_get_one(
        self, secret: str, identifier: str
    ) -> dict[str, Any]:
        return await self._make_request("dataquery", "getone", [secret, identifier])

    # -- Staff ----------------------------------------------------------------

    async def get_all_staff_data(self) -> dict[str, Any]:
        if not Config.ADAM_DATAQUERY_STAFF_SECRET:
            raise AdamAPIError("ADAM_DATAQUERY_STAFF_SECRET not configured")
        return await self._make_request(
            "dataquery", "get", [Config.ADAM_DATAQUERY_STAFF_SECRET]
        )

    async def find_staff_by_name(self, name: str) -> list[dict[str, Any]]:
        data = await self.get_all_staff_data()
        search_words = name.lower().strip().split()
        results: list[dict[str, Any]] = []
        for record in data.values():
            last_name = record.get("last_name_31", "").lower()
            preferred_name = record.get("first_name_preferred_32", "").lower()
            full_name = record.get("full_first_name_142", "").lower()
            combined = f"{last_name} {preferred_name} {full_name}"
            if all(w in combined for w in search_words):
                results.append(
                    {
                        "staff_id": record.get("adam_identifier_284"),
                        "admin_no": record.get("admin_no_30"),
                        "last_name": record.get("last_name_31"),
                        "preferred_name": record.get("first_name_preferred_32"),
                        "full_name": record.get("full_first_name_142"),
                        "position": record.get("position_233"),
                        "department": record.get("department_49"),
                        "email": record.get("email_address_67"),
                    }
                )
        return results

    # -- Data Query (name lookups) --------------------------------------------

    async def get_all_pupils_data(self) -> dict[str, Any]:
        if not Config.ADAM_DATAQUERY_PUPILS_SECRET:
            raise AdamAPIError("ADAM_DATAQUERY_PUPILS_SECRET not configured")
        return await self._make_request(
            "dataquery", "get", [Config.ADAM_DATAQUERY_PUPILS_SECRET]
        )

    async def get_all_families_data(self) -> dict[str, Any]:
        if not Config.ADAM_DATAQUERY_FAMILIES_SECRET:
            raise AdamAPIError("ADAM_DATAQUERY_FAMILIES_SECRET not configured")
        return await self._make_request(
            "dataquery", "get", [Config.ADAM_DATAQUERY_FAMILIES_SECRET]
        )

    async def find_pupils_by_name(self, name: str) -> list[dict[str, Any]]:
        data = await self.get_all_pupils_data()
        search_words = name.lower().strip().split()
        results: list[dict[str, Any]] = []
        for record in data.values():
            last_name = record.get("last_name_2", "").lower()
            preferred_name = record.get("preferred_name_3", "").lower()
            full_first_names = record.get("full_first_names_4", "").lower()
            combined = f"{last_name} {preferred_name} {full_first_names}"
            if all(w in combined for w in search_words):
                results.append(
                    {
                        "pupil_id": record.get("adam_id_257"),
                        "admin_number": record.get("admin_number_1"),
                        "last_name": record.get("last_name_2"),
                        "preferred_name": record.get("preferred_name_3"),
                        "full_first_names": record.get("full_first_names_4"),
                        "grade": record.get("grade_9"),
                        "email": record.get("email_21"),
                    }
                )
        return results

    async def find_families_by_name(self, name: str) -> list[dict[str, Any]]:
        data = await self.get_all_families_data()
        search_words = name.lower().strip().split()
        results: list[dict[str, Any]] = []
        for record in data.values():
            family_surname = record.get("family_greeting_surname_133", "").lower()
            family_first_names = record.get(
                "family_greeting_first_names_143", ""
            ).lower()
            address_name = record.get("family_address_name_132", "").lower()
            father_greeting = record.get("father_039_s_greeting_288", "").lower()
            mother_greeting = record.get("mother_039_s_greeting_289", "").lower()
            combined = f"{family_surname} {family_first_names} {address_name} {father_greeting} {mother_greeting}"
            if all(w in combined for w in search_words):
                results.append(
                    {
                        "family_id": record.get("family_identifier_253"),
                        "family_surname": record.get("family_greeting_surname_133"),
                        "family_first_names": record.get(
                            "family_greeting_first_names_143"
                        ),
                        "address_name": record.get("family_address_name_132"),
                        "father_greeting": record.get("father_039_s_greeting_288"),
                        "mother_greeting": record.get("mother_039_s_greeting_289"),
                    }
                )
        return results


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


def _output_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _output_text(data: Any) -> str:
    if isinstance(data, list):
        lines: list[str] = []
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                lines.append(f"--- {i} ---")
                for k, v in item.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(str(item))
        return "\n".join(lines) if lines else "(empty)"
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{k}:")
                lines.append(f"  {json.dumps(v, indent=2, ensure_ascii=False)}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines) if lines else "(empty)"
    return str(data)


def _output_csv(data: Any) -> str:
    if isinstance(data, list) and data and isinstance(data[0], dict):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return buf.getvalue()
    if isinstance(data, dict):
        # Single record: key,value
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["key", "value"])
        for k, v in data.items():
            writer.writerow([k, json.dumps(v) if isinstance(v, (dict, list)) else v])
        return buf.getvalue()
    return str(data)


def _format_output(data: Any, fmt: str) -> str:
    if fmt == "text":
        return _output_text(data)
    if fmt == "csv":
        return _output_csv(data)
    return _output_json(data)


# ---------------------------------------------------------------------------
# CLI command handlers
# ---------------------------------------------------------------------------


async def cmd_test(client: AdamAPIClient, _args: argparse.Namespace) -> Any:
    return await client.test_connection()


# -- Pupils --

async def cmd_pupils_find(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.find_pupils_by_name(args.name)


async def cmd_pupils_info(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_pupil_info(args.pupil_id)


async def cmd_pupils_classes(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_pupil_classes(args.pupil_id)


async def cmd_pupils_contacts(client: AdamAPIClient, _args: argparse.Namespace) -> Any:
    return await client.get_all_pupil_contacts()


async def cmd_pupils_search_id(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.search_pupil_by_id_number(args.id_number)


async def cmd_pupils_fields(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_pupil_fields(getattr(args, "action", None))


async def cmd_pupils_search_admin(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.search_pupil_admin(args.search_term)


# -- Calendar --

async def cmd_calendar_pupil_links(
    client: AdamAPIClient, _args: argparse.Namespace
) -> Any:
    return await client.get_calendar_pupil_links()


async def cmd_calendar_staff_links(
    client: AdamAPIClient, _args: argparse.Namespace
) -> Any:
    return await client.get_calendar_staff_links()


# -- Academics --

async def cmd_academics_record(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_pupil_academic_records(args.pupil_id)


async def cmd_academics_assessments(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_recent_assessment_results(args.pupil_id)


async def cmd_academics_markbook(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_pupil_markbook(args.period_id, args.pupil_id)


async def cmd_academics_periods(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_reporting_periods(getattr(args, "year", None))


async def cmd_academics_pupil_periods(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_pupil_reporting_periods(args.pupil_id)


async def cmd_academics_results(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_reporting_results(args.period_id)


async def cmd_academics_previous_reports(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_previous_reports(args.pupil_id)


async def cmd_academics_question_breakdown(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_question_breakdown(args.assessment_id)


# -- Teachers --

async def cmd_teachers_emails(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_pupil_teachers(args.pupil_id)


async def cmd_teachers_classes(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_pupil_classes(args.pupil_id)


# -- Families --

async def cmd_families_find(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.find_families_by_name(args.name)


async def cmd_families_emails(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_family_emails(args.family_id)


async def cmd_families_children(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_family_children(args.family_id)


async def cmd_families_relationships(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_pupil_family_relationships(args.pupil_id)


async def cmd_families_contacts(
    client: AdamAPIClient, _args: argparse.Namespace
) -> Any:
    return await client.get_all_family_contacts()


async def cmd_families_current_children(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_family_current_children(args.family_id)


async def cmd_families_search_id(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.search_family_by_id_number(args.id_number)


async def cmd_families_relationship_types(
    client: AdamAPIClient, _args: argparse.Namespace
) -> Any:
    return await client.get_family_relationship_types()


async def cmd_families_family_relationships(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_family_relationships(args.family_id)


async def cmd_families_login_privileges(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_family_login_privileges(args.family_id)


# -- Classes --

async def cmd_classes_list(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    regs = await client.get_grade_registrations(args.grade)
    if isinstance(regs, dict):
        regs = regs.get("data", regs)
    if not isinstance(regs, list):
        return []
    classes: dict[str, dict] = {}
    for reg in regs:
        desc = reg.get("class_description", "")
        if desc not in classes:
            classes[desc] = {
                "class_description": desc,
                "class_id": reg.get("class_id"),
                "subject": reg.get("subject_name", ""),
                "pupil_count": 0,
            }
        classes[desc]["pupil_count"] += 1
    return sorted(classes.values(), key=lambda c: c["class_description"])


async def cmd_classes_parent_emails(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_class_parent_emails(args.grade, args.class_description)


async def cmd_classes_by_grade_period_subject(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_classes_by_grade_period_subject(
        args.grade, args.period_id, args.subject_id
    )


# -- Attendance --

async def cmd_attendance_summary(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_absence_summary(args.start_date, args.end_date)


async def cmd_attendance_list(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_absence_list(args.start_date, args.end_date)


async def cmd_attendance_pupil_days(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_pupil_days_absent(
        args.pupil_id, getattr(args, "year", None)
    )


# -- Leaves --

async def cmd_leaves_approved(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_approved_leaves(
        getattr(args, "start_date", None), getattr(args, "end_date", None)
    )


# -- Records --

async def cmd_records_recent(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_recent_pupil_records(args.pupil_id)


async def cmd_records_by_date(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_pupil_records_date_range(
        args.pupil_id,
        getattr(args, "start_date", None),
        getattr(args, "end_date", None),
    )


# -- Staff --

async def cmd_staff_find(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.find_staff_by_name(args.name)


# -- Medical --

async def cmd_medical_off_sport(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_off_sport_list(getattr(args, "date", None))


# -- Subjects --

async def cmd_subjects_by_grade(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_subjects_by_grade(args.grade)


async def cmd_subjects_by_grades(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_subjects_by_grades(args.grades)


# -- Psychometric --

async def cmd_psychometric_assessments(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.get_psychometric_assessments(
        getattr(args, "pupil_id", None), getattr(args, "category_id", None)
    )


# -- Messages --

async def cmd_messages_list(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_messages(
        getattr(args, "start_date", None), getattr(args, "end_date", None)
    )


async def cmd_messages_get(client: AdamAPIClient, args: argparse.Namespace) -> Any:
    return await client.get_message(args.message_id)


# -- Admissions --

async def cmd_admissions_status_list(
    client: AdamAPIClient, _args: argparse.Namespace
) -> Any:
    return await client.get_registration_status_list()


async def cmd_admissions_statuses(
    client: AdamAPIClient, _args: argparse.Namespace
) -> Any:
    return await client.get_registration_statuses()


# -- Data Query --

async def cmd_dataquery_get_one(
    client: AdamAPIClient, args: argparse.Namespace
) -> Any:
    return await client.dataquery_get_one(args.secret, args.identifier)


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adam",
        description="CLI for ADAM School Management Information System",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "text", "csv"],
        default="json",
        help="Output format (default: json)",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # test
    p = sub.add_parser("test", help="Test API connection")
    p.set_defaults(func=cmd_test)

    # -- pupils ---------------------------------------------------------------
    pupils = sub.add_parser("pupils", help="Pupil information")
    pupils_sub = pupils.add_subparsers(dest="subcommand")

    p = pupils_sub.add_parser("find", help="Search pupils by name")
    p.add_argument("name", help="Name to search (partial, case-insensitive)")
    p.set_defaults(func=cmd_pupils_find)

    p = pupils_sub.add_parser("info", help="Get pupil details")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_pupils_info)

    p = pupils_sub.add_parser("classes", help="Get pupil's classes and teachers")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_pupils_classes)

    p = pupils_sub.add_parser("contacts", help="Get all pupil contacts")
    p.set_defaults(func=cmd_pupils_contacts)

    p = pupils_sub.add_parser("search-id", help="Search pupil by ID number")
    p.add_argument("id_number", help="ID number to search")
    p.set_defaults(func=cmd_pupils_search_id)

    p = pupils_sub.add_parser("fields", help="Get pupil field definitions")
    p.add_argument("action", nargs="?", help="Action type (add, edit, view)")
    p.set_defaults(func=cmd_pupils_fields)

    p = pupils_sub.add_parser("search-admin", help="Search pupils by admin identifier")
    p.add_argument("search_term", help="Administrative search term")
    p.set_defaults(func=cmd_pupils_search_admin)

    # -- calendar -------------------------------------------------------------
    calendar = sub.add_parser("calendar", help="Calendar links")
    calendar_sub = calendar.add_subparsers(dest="subcommand")

    p = calendar_sub.add_parser("pupil-links", help="Get pupil calendar links")
    p.set_defaults(func=cmd_calendar_pupil_links)

    p = calendar_sub.add_parser("staff-links", help="Get staff calendar links")
    p.set_defaults(func=cmd_calendar_staff_links)

    # -- academics ------------------------------------------------------------
    academics = sub.add_parser("academics", help="Academic records and assessments")
    academics_sub = academics.add_subparsers(dest="subcommand")

    p = academics_sub.add_parser("record", help="Get pupil academic records")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_academics_record)

    p = academics_sub.add_parser("assessments", help="Get recent assessment results")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_academics_assessments)

    p = academics_sub.add_parser("markbook", help="Get markbook for a period")
    p.add_argument("period_id", help="Reporting period ID")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_academics_markbook)

    p = academics_sub.add_parser("periods", help="Get reporting periods")
    p.add_argument("year", nargs="?", help="Year (e.g. 2024)")
    p.set_defaults(func=cmd_academics_periods)

    p = academics_sub.add_parser(
        "pupil-periods", help="Get reporting periods for a pupil"
    )
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_academics_pupil_periods)

    p = academics_sub.add_parser("results", help="Get all results for a period")
    p.add_argument("period_id", help="Reporting period ID")
    p.set_defaults(func=cmd_academics_results)

    p = academics_sub.add_parser(
        "previous-reports", help="Get list of previous reports for a pupil"
    )
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_academics_previous_reports)

    p = academics_sub.add_parser(
        "question-breakdown", help="Get question breakdown for an assessment"
    )
    p.add_argument("assessment_id", help="Assessment ID")
    p.set_defaults(func=cmd_academics_question_breakdown)

    # -- teachers -------------------------------------------------------------
    teachers = sub.add_parser("teachers", help="Teacher information")
    teachers_sub = teachers.add_subparsers(dest="subcommand")

    p = teachers_sub.add_parser("emails", help="Get pupil's teachers and emails")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_teachers_emails)

    p = teachers_sub.add_parser("classes", help="Get pupil's classes with teachers")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_teachers_classes)

    # -- families -------------------------------------------------------------
    families = sub.add_parser("families", help="Family information")
    families_sub = families.add_subparsers(dest="subcommand")

    p = families_sub.add_parser("find", help="Search families by name")
    p.add_argument("name", help="Name to search (partial, case-insensitive)")
    p.set_defaults(func=cmd_families_find)

    p = families_sub.add_parser("emails", help="Get family email addresses")
    p.add_argument("family_id", help="Family ID")
    p.set_defaults(func=cmd_families_emails)

    p = families_sub.add_parser("children", help="Get children in a family")
    p.add_argument("family_id", help="Family ID")
    p.set_defaults(func=cmd_families_children)

    p = families_sub.add_parser(
        "relationships", help="Get family relationships for a pupil"
    )
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_families_relationships)

    p = families_sub.add_parser("contacts", help="Get all family contacts")
    p.set_defaults(func=cmd_families_contacts)

    p = families_sub.add_parser(
        "current-children", help="Get currently enrolled children in a family"
    )
    p.add_argument("family_id", help="Family ID")
    p.set_defaults(func=cmd_families_current_children)

    p = families_sub.add_parser("search-id", help="Search family by ID number")
    p.add_argument("id_number", help="ID number to search")
    p.set_defaults(func=cmd_families_search_id)

    p = families_sub.add_parser(
        "relationship-types", help="Get family relationship type definitions"
    )
    p.set_defaults(func=cmd_families_relationship_types)

    p = families_sub.add_parser(
        "family-relationships", help="Get relationship details for a family"
    )
    p.add_argument("family_id", help="Family ID")
    p.set_defaults(func=cmd_families_family_relationships)

    p = families_sub.add_parser(
        "login-privileges", help="Get family login privileges"
    )
    p.add_argument("family_id", help="Family ID")
    p.set_defaults(func=cmd_families_login_privileges)

    # -- classes --------------------------------------------------------------
    classes = sub.add_parser("classes", help="Class information")
    classes_sub = classes.add_subparsers(dest="subcommand")

    p = classes_sub.add_parser("list", help="List classes for a grade")
    p.add_argument("grade", help="Grade level (e.g. 8, 9, 10)")
    p.set_defaults(func=cmd_classes_list)

    p = classes_sub.add_parser("parent-emails", help="Get parent emails for a class")
    p.add_argument("grade", help="Grade level (e.g. 8, 9, 10)")
    p.add_argument("class_description", help="Class description (partial match)")
    p.set_defaults(func=cmd_classes_parent_emails)

    p = classes_sub.add_parser(
        "by-grade-period-subject", help="Get classes by grade, period, and subject"
    )
    p.add_argument("grade", help="Grade level")
    p.add_argument("period_id", help="Reporting period ID")
    p.add_argument("subject_id", help="Subject ID")
    p.set_defaults(func=cmd_classes_by_grade_period_subject)

    # -- attendance -----------------------------------------------------------
    attendance = sub.add_parser("attendance", help="Attendance records")
    attendance_sub = attendance.add_subparsers(dest="subcommand")

    p = attendance_sub.add_parser("summary", help="Get absence summary")
    p.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    p.add_argument("end_date", help="End date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_attendance_summary)

    p = attendance_sub.add_parser("list", help="Get detailed absence list")
    p.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    p.add_argument("end_date", help="End date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_attendance_list)

    p = attendance_sub.add_parser("pupil-days", help="Get days absent for a pupil")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.add_argument("year", nargs="?", help="Year to filter by (e.g. 2024)")
    p.set_defaults(func=cmd_attendance_pupil_days)

    # -- leaves ---------------------------------------------------------------
    leaves = sub.add_parser("leaves", help="Leave requests")
    leaves_sub = leaves.add_subparsers(dest="subcommand")

    p = leaves_sub.add_parser("approved", help="Get approved leave requests")
    p.add_argument("start_date", nargs="?", help="Start date (YYYY-MM-DD)")
    p.add_argument("end_date", nargs="?", help="End date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_leaves_approved)

    # -- records --------------------------------------------------------------
    records = sub.add_parser("records", help="Behaviour and achievement records")
    records_sub = records.add_subparsers(dest="subcommand")

    p = records_sub.add_parser("recent", help="Get recent records for a pupil")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.set_defaults(func=cmd_records_recent)

    p = records_sub.add_parser("by-date", help="Get records by date range")
    p.add_argument("pupil_id", help="Pupil ID or admission number")
    p.add_argument("start_date", nargs="?", help="Start date (YYYY-MM-DD)")
    p.add_argument("end_date", nargs="?", help="End date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_records_by_date)

    # -- staff ----------------------------------------------------------------
    staff = sub.add_parser("staff", help="Staff information")
    staff_sub = staff.add_subparsers(dest="subcommand")

    p = staff_sub.add_parser("find", help="Search staff by name")
    p.add_argument("name", help="Name to search (partial, case-insensitive)")
    p.set_defaults(func=cmd_staff_find)

    # -- medical --------------------------------------------------------------
    medical = sub.add_parser("medical", help="Medical information")
    medical_sub = medical.add_subparsers(dest="subcommand")

    p = medical_sub.add_parser("off-sport", help="Get off-sport list")
    p.add_argument("date", nargs="?", help="Date (YYYY-MM-DD, default: today)")
    p.set_defaults(func=cmd_medical_off_sport)

    # -- subjects -------------------------------------------------------------
    subjects = sub.add_parser("subjects", help="Subject information")
    subjects_sub = subjects.add_subparsers(dest="subcommand")

    p = subjects_sub.add_parser("by-grade", help="Get subjects for a grade")
    p.add_argument("grade", help="Grade level (e.g. 8, 9, 10)")
    p.set_defaults(func=cmd_subjects_by_grade)

    p = subjects_sub.add_parser("by-grades", help="Get subjects for multiple grades")
    p.add_argument("grades", help="Comma-separated grades (e.g. 8,9,10)")
    p.set_defaults(func=cmd_subjects_by_grades)

    # -- psychometric ---------------------------------------------------------
    psychometric = sub.add_parser("psychometric", help="Psychometric assessments")
    psychometric_sub = psychometric.add_subparsers(dest="subcommand")

    p = psychometric_sub.add_parser(
        "assessments", help="Get psychometric assessments by category"
    )
    p.add_argument("pupil_id", nargs="?", help="Pupil ID (optional)")
    p.add_argument("category_id", nargs="?", help="Category ID (optional)")
    p.set_defaults(func=cmd_psychometric_assessments)

    # -- messages -------------------------------------------------------------
    messages = sub.add_parser("messages", help="Messaging logs")
    messages_sub = messages.add_subparsers(dest="subcommand")

    p = messages_sub.add_parser("list", help="Get messaging logs")
    p.add_argument("start_date", nargs="?", help="Start date (YYYY-MM-DD)")
    p.add_argument("end_date", nargs="?", help="End date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_messages_list)

    p = messages_sub.add_parser("get", help="Get a specific message")
    p.add_argument("message_id", help="Message ID")
    p.set_defaults(func=cmd_messages_get)

    # -- admissions -----------------------------------------------------------
    admissions = sub.add_parser("admissions", help="Admissions and registration")
    admissions_sub = admissions.add_subparsers(dest="subcommand")

    p = admissions_sub.add_parser("status-list", help="Get registration status types")
    p.set_defaults(func=cmd_admissions_status_list)

    p = admissions_sub.add_parser("statuses", help="Get all pupil registration statuses")
    p.set_defaults(func=cmd_admissions_statuses)

    # -- dataquery ------------------------------------------------------------
    dataquery = sub.add_parser("dataquery", help="Data Query API")
    dataquery_sub = dataquery.add_subparsers(dest="subcommand")

    p = dataquery_sub.add_parser("get-one", help="Get single record from data query")
    p.add_argument("secret", help="Data query secret key")
    p.add_argument("identifier", help="Individual ID")
    p.set_defaults(func=cmd_dataquery_get_one)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def _async_main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help(sys.stderr)
        return 1

    if not hasattr(args, "func"):
        # Subcommand group selected but no subcommand given
        parser.parse_args([args.command, "--help"])
        return 1

    Config.validate()
    client = AdamAPIClient()

    try:
        result = await args.func(client, args)
        output = _format_output(result, args.format)
        print(output)
        return 0
    except AdamAPIError as e:
        print(json.dumps({"error": e.message}), file=sys.stderr)
        return 1
    except BrokenPipeError:
        # Handle piping to head/less etc.
        return 0


def main() -> None:
    # Handle SIGPIPE gracefully (for piping to head, etc.)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    try:
        code = asyncio.run(_async_main())
    except KeyboardInterrupt:
        code = 130

    sys.exit(code)


if __name__ == "__main__":
    main()
