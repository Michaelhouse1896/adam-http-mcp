/**
 * ADAM API tool definitions.
 *
 * Each entry describes one MCP tool that maps to an ADAM REST API call.
 * Simple tools use `module`, `resource`, and `params` to build the URL via
 * the standard path-segment pattern:  /api/{module}/{resource}/{p1}/{p2}/...
 *
 * Complex tools set `handler: "custom"` and are implemented directly in index.ts.
 */

export interface ToolParam {
  name: string;
  type: "string" | "number";
  required: boolean;
  description: string;
}

export interface ToolDef {
  toolName: string;
  description: string;
  params: ToolParam[];
  /** ADAM API module (first path segment after /api/) */
  module?: string;
  /** ADAM API resource (second path segment) */
  resource?: string;
  /** Ordered list of param names that become path segments */
  pathParams?: string[];
  /** If set, this tool has a custom handler in index.ts */
  handler?: "custom";
}

export const tools: ToolDef[] = [
  // ---------------------------------------------------------------------------
  // Test
  // ---------------------------------------------------------------------------
  {
    toolName: "test_connection",
    description: "Test connectivity to the ADAM API. Returns success/failure status.",
    params: [],
    module: "request",
    resource: "test",
    pathParams: [],
  },

  // ---------------------------------------------------------------------------
  // Pupils
  // ---------------------------------------------------------------------------
  {
    toolName: "pupils_find",
    description:
      "Search pupils by name (partial, case-insensitive, multi-word). Requires ADAM_DATAQUERY_PUPILS_SECRET. Returns pupil_id, admin_number, names, grade, email.",
    params: [
      { name: "name", type: "string", required: true, description: "Name to search for" },
    ],
    handler: "custom",
  },
  {
    toolName: "pupils_info",
    description: "Get detailed information for a specific pupil.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "pupils",
    resource: "pupil",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "pupils_classes",
    description: "Get a pupil's classes and their teachers.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "classes",
    resource: "pupilteachers",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "pupils_contacts",
    description: "Get the full pupil contact list.",
    params: [],
    module: "pupils",
    resource: "contactlist",
    pathParams: [],
  },
  {
    toolName: "pupils_search_id",
    description: "Search for a pupil by their ID number (e.g. national ID).",
    params: [
      { name: "id_number", type: "string", required: true, description: "ID number to search" },
    ],
    module: "pupils",
    resource: "searchbyid",
    pathParams: ["id_number"],
  },
  {
    toolName: "pupils_fields",
    description: "Get pupil field definitions. Optionally filter by action type.",
    params: [
      { name: "action", type: "string", required: false, description: "Action type: add, edit, or view" },
    ],
    module: "pupils",
    resource: "fields",
    pathParams: ["action"],
  },
  {
    toolName: "pupils_search_admin",
    description: "Search pupils by administrative identifier.",
    params: [
      { name: "search_term", type: "string", required: true, description: "Administrative search term" },
    ],
    module: "pupils",
    resource: "search-admin",
    pathParams: ["search_term"],
  },

  // ---------------------------------------------------------------------------
  // Calendar
  // ---------------------------------------------------------------------------
  {
    toolName: "calendar_pupil_links",
    description: "Get calendar subscription links for pupils.",
    params: [],
    module: "calendar",
    resource: "pupillinks",
    pathParams: [],
  },
  {
    toolName: "calendar_staff_links",
    description: "Get calendar subscription links for staff.",
    params: [],
    module: "calendar",
    resource: "stafflinks",
    pathParams: [],
  },

  // ---------------------------------------------------------------------------
  // Academics
  // ---------------------------------------------------------------------------
  {
    toolName: "academics_record",
    description: "Get academic subject marks and records for a pupil.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "reporting",
    resource: "subjectmarksbypupil",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "academics_assessments",
    description: "Get recent assessment results for a pupil.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "assessment",
    resource: "recentresults",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "academics_markbook",
    description: "Get the markbook for a specific reporting period and pupil.",
    params: [
      { name: "period_id", type: "string", required: true, description: "Reporting period ID" },
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "reporting",
    resource: "markbook",
    pathParams: ["period_id", "pupil_id"],
  },
  {
    toolName: "academics_periods",
    description: "Get reporting periods. Optionally filter by year.",
    params: [
      { name: "year", type: "string", required: false, description: "Year (e.g. 2024)" },
    ],
    module: "reporting",
    resource: "periods",
    pathParams: ["year"],
  },
  {
    toolName: "academics_pupil_periods",
    description: "Get reporting periods available for a specific pupil.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "reporting",
    resource: "pupilreportingperiods",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "academics_results",
    description: "Get all results for a reporting period.",
    params: [
      { name: "period_id", type: "string", required: true, description: "Reporting period ID" },
    ],
    module: "reporting",
    resource: "results",
    pathParams: ["period_id"],
  },
  {
    toolName: "academics_previous_reports",
    description: "Get list of previous reports for a pupil.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "reporting",
    resource: "previousreports",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "academics_question_breakdown",
    description: "Get question-level breakdown for an assessment.",
    params: [
      { name: "assessment_id", type: "string", required: true, description: "Assessment ID" },
    ],
    module: "questions",
    resource: "questionbreakdown",
    pathParams: ["assessment_id"],
  },

  // ---------------------------------------------------------------------------
  // Teachers
  // ---------------------------------------------------------------------------
  {
    toolName: "teachers_emails",
    description: "Get a pupil's teachers and their email addresses.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "classes",
    resource: "pupilteachers",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "teachers_classes",
    description: "Get a pupil's classes with teacher information.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "classes",
    resource: "pupilteachers",
    pathParams: ["pupil_id"],
  },

  // ---------------------------------------------------------------------------
  // Families
  // ---------------------------------------------------------------------------
  {
    toolName: "families_find",
    description:
      "Search families by name (partial, case-insensitive, multi-word). Requires ADAM_DATAQUERY_FAMILIES_SECRET.",
    params: [
      { name: "name", type: "string", required: true, description: "Name to search for" },
    ],
    handler: "custom",
  },
  {
    toolName: "families_emails",
    description: "Get email addresses for a family.",
    params: [
      { name: "family_id", type: "string", required: true, description: "Family ID" },
    ],
    module: "families",
    resource: "email",
    pathParams: ["family_id"],
  },
  {
    toolName: "families_children",
    description: "Get all children in a family.",
    params: [
      { name: "family_id", type: "string", required: true, description: "Family ID" },
    ],
    module: "families",
    resource: "children",
    pathParams: ["family_id"],
  },
  {
    toolName: "families_relationships",
    description: "Get family relationships for a pupil.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "familyrelationships",
    resource: "pupil",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "families_contacts",
    description: "Get the full family contact list.",
    params: [],
    module: "families",
    resource: "contactlist",
    pathParams: [],
  },
  {
    toolName: "families_current_children",
    description: "Get currently enrolled children in a family.",
    params: [
      { name: "family_id", type: "string", required: true, description: "Family ID" },
    ],
    module: "families",
    resource: "currentchildren",
    pathParams: ["family_id"],
  },
  {
    toolName: "families_search_id",
    description: "Search for a family by ID number.",
    params: [
      { name: "id_number", type: "string", required: true, description: "ID number to search" },
    ],
    module: "families",
    resource: "searchbyid",
    pathParams: ["id_number"],
  },
  {
    toolName: "families_relationship_types",
    description: "Get family relationship type definitions.",
    params: [],
    module: "families",
    resource: "familyrelationships",
    pathParams: [],
  },
  {
    toolName: "families_family_relationships",
    description: "Get relationship details for a specific family.",
    params: [
      { name: "family_id", type: "string", required: true, description: "Family ID" },
    ],
    module: "familyrelationships",
    resource: "family",
    pathParams: ["family_id"],
  },
  {
    toolName: "families_login_privileges",
    description: "Get family login privileges.",
    params: [
      { name: "family_id", type: "string", required: true, description: "Family ID" },
    ],
    module: "familylogin",
    resource: "privileges",
    pathParams: ["family_id"],
  },

  // ---------------------------------------------------------------------------
  // Classes
  // ---------------------------------------------------------------------------
  {
    toolName: "classes_list",
    description:
      "List deduplicated classes for a grade with pupil counts. Shows class_description, class_id, subject, and pupil_count.",
    params: [
      { name: "grade", type: "string", required: true, description: "Grade level (e.g. 8, 9, 10)" },
    ],
    handler: "custom",
  },
  {
    toolName: "classes_parent_emails",
    description:
      "Get all parent email addresses for pupils in a class. Chains grade registrations → family relationships → family emails. Returns per-pupil family emails and a deduplicated all_emails list.",
    params: [
      { name: "grade", type: "string", required: true, description: "Grade level (e.g. 8, 9, 10)" },
      { name: "class_description", type: "string", required: true, description: "Class description (partial, case-insensitive match)" },
    ],
    handler: "custom",
  },
  {
    toolName: "classes_by_grade_period_subject",
    description: "Get classes by grade, reporting period, and subject.",
    params: [
      { name: "grade", type: "string", required: true, description: "Grade level" },
      { name: "period_id", type: "string", required: true, description: "Reporting period ID" },
      { name: "subject_id", type: "string", required: true, description: "Subject ID" },
    ],
    module: "classes",
    resource: "bygradeperiodsubject",
    pathParams: ["grade", "period_id", "subject_id"],
  },

  // ---------------------------------------------------------------------------
  // Attendance
  // ---------------------------------------------------------------------------
  {
    toolName: "attendance_summary",
    description: "Get absence summary counts for a date range.",
    params: [
      { name: "start_date", type: "string", required: true, description: "Start date (YYYY-MM-DD)" },
      { name: "end_date", type: "string", required: true, description: "End date (YYYY-MM-DD)" },
    ],
    module: "absentees",
    resource: "summarycount",
    pathParams: ["start_date", "end_date"],
  },
  {
    toolName: "attendance_list",
    description: "Get detailed absence list for a date range.",
    params: [
      { name: "start_date", type: "string", required: true, description: "Start date (YYYY-MM-DD)" },
      { name: "end_date", type: "string", required: true, description: "End date (YYYY-MM-DD)" },
    ],
    module: "absentees",
    resource: "list",
    pathParams: ["start_date", "end_date"],
  },
  {
    toolName: "attendance_pupil_days",
    description: "Get days absent for a specific pupil. Optionally filter by year.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
      { name: "year", type: "string", required: false, description: "Year to filter by (e.g. 2024)" },
    ],
    module: "absentees",
    resource: "daysabsentforpupil",
    pathParams: ["pupil_id", "year"],
  },

  // ---------------------------------------------------------------------------
  // Leaves
  // ---------------------------------------------------------------------------
  {
    toolName: "leaves_approved",
    description:
      "Get approved leave requests. Optionally filter by pupil and/or date range (client-side filtering).",
    params: [
      { name: "pupil_id", type: "string", required: false, description: "Pupil ID (omit for all)" },
      { name: "start_date", type: "string", required: false, description: "Filter from date (YYYY-MM-DD, inclusive)" },
      { name: "end_date", type: "string", required: false, description: "Filter to date (YYYY-MM-DD, inclusive)" },
    ],
    handler: "custom",
  },

  // ---------------------------------------------------------------------------
  // Records
  // ---------------------------------------------------------------------------
  {
    toolName: "records_recent",
    description: "Get recent behaviour and achievement records for a pupil.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
    ],
    module: "recordsandpoints",
    resource: "recentpupilrecords",
    pathParams: ["pupil_id"],
  },
  {
    toolName: "records_by_date",
    description: "Get pupil records filtered by date range.",
    params: [
      { name: "pupil_id", type: "string", required: true, description: "Pupil ID or admission number" },
      { name: "start_date", type: "string", required: false, description: "Start date (YYYY-MM-DD)" },
      { name: "end_date", type: "string", required: false, description: "End date (YYYY-MM-DD)" },
    ],
    module: "recordsandpoints",
    resource: "pupilrecords",
    pathParams: ["pupil_id", "start_date", "end_date"],
  },

  // ---------------------------------------------------------------------------
  // Staff
  // ---------------------------------------------------------------------------
  {
    toolName: "staff_find",
    description:
      "Search staff by name (partial, case-insensitive, multi-word). Requires ADAM_DATAQUERY_STAFF_SECRET.",
    params: [
      { name: "name", type: "string", required: true, description: "Name to search for" },
    ],
    handler: "custom",
  },

  // ---------------------------------------------------------------------------
  // Medical
  // ---------------------------------------------------------------------------
  {
    toolName: "medical_off_sport",
    description: "Get list of pupils excused from sport. Optionally filter by date.",
    params: [
      { name: "date", type: "string", required: false, description: "Date (YYYY-MM-DD, default: today)" },
    ],
    module: "medical",
    resource: "offsport",
    pathParams: ["date"],
  },

  // ---------------------------------------------------------------------------
  // Subjects
  // ---------------------------------------------------------------------------
  {
    toolName: "subjects_by_grade",
    description: "Get subjects offered for a specific grade.",
    params: [
      { name: "grade", type: "string", required: true, description: "Grade level (e.g. 8, 9, 10)" },
    ],
    module: "subjects",
    resource: "get_by_grade",
    pathParams: ["grade"],
  },
  {
    toolName: "subjects_by_grades",
    description: "Get subjects offered across multiple grades.",
    params: [
      { name: "grades", type: "string", required: true, description: "Comma-separated grades (e.g. 8,9,10)" },
    ],
    module: "subjects",
    resource: "get_by_grades",
    pathParams: ["grades"],
  },

  // ---------------------------------------------------------------------------
  // Psychometric
  // ---------------------------------------------------------------------------
  {
    toolName: "psychometric_assessments",
    description: "Get psychometric assessments by category. Both parameters are optional.",
    params: [
      { name: "pupil_id", type: "string", required: false, description: "Pupil ID" },
      { name: "category_id", type: "string", required: false, description: "Category ID" },
    ],
    module: "psychometric",
    resource: "assessmentsbycategory",
    pathParams: ["pupil_id", "category_id"],
  },

  // ---------------------------------------------------------------------------
  // Messages
  // ---------------------------------------------------------------------------
  {
    toolName: "messages_list",
    description: "Get messaging logs. Optionally filter by date range.",
    params: [
      { name: "start_date", type: "string", required: false, description: "Start date (YYYY-MM-DD)" },
      { name: "end_date", type: "string", required: false, description: "End date (YYYY-MM-DD)" },
    ],
    module: "messaginglogs",
    resource: "messages",
    pathParams: ["start_date", "end_date"],
  },
  {
    toolName: "messages_get",
    description: "Get a specific message by ID.",
    params: [
      { name: "message_id", type: "string", required: true, description: "Message ID" },
    ],
    module: "messaginglogs",
    resource: "message",
    pathParams: ["message_id"],
  },

  // ---------------------------------------------------------------------------
  // Admissions
  // ---------------------------------------------------------------------------
  {
    toolName: "admissions_status_list",
    description: "Get registration status type definitions.",
    params: [],
    module: "registration",
    resource: "statuslist",
    pathParams: [],
  },
  {
    toolName: "admissions_statuses",
    description: "Get all pupil registration statuses.",
    params: [],
    module: "registration",
    resource: "statuses",
    pathParams: [],
  },

  // ---------------------------------------------------------------------------
  // Data Query — full record lookups (secret resolved internally)
  // ---------------------------------------------------------------------------
  {
    toolName: "staff_data",
    description:
      "Get the full data query record for a staff member by identifier. Returns ALL fields. Use staff_find first to get the identifier.",
    params: [
      { name: "identifier", type: "string", required: true, description: "Staff adam_identifier (use staff_find first to obtain this)" },
    ],
    handler: "custom",
  },
  {
    toolName: "pupils_data",
    description:
      "Get the full data query record for a pupil by identifier. Returns ALL fields. Use pupils_find or pupils_search_admin first to get the identifier.",
    params: [
      { name: "identifier", type: "string", required: true, description: "Pupil adam_id (use pupils_find or pupils_search_admin first to obtain this)" },
    ],
    handler: "custom",
  },
  {
    toolName: "families_data",
    description:
      "Get the full data query record for a family by identifier. Returns ALL fields. Use families_find first to get the identifier.",
    params: [
      { name: "identifier", type: "string", required: true, description: "Family identifier" },
    ],
    handler: "custom",
  },
];
