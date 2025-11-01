# ADAM API Endpoints Documentation

## Overview
This document provides comprehensive details for all 70+ API endpoints in the ADAM (Academic Data Manager) system. Each endpoint includes implementation details, parameters, authorization requirements, and examples.

**Base URL**: `/api/` or `/apicore/`

**Authentication**: Most endpoints require an API token passed in the request headers.

**Parameter Format**: Path parameters are separated by `/` in the URL path (e.g., `/api/pupils/pupil/123`)

---

## Table of Contents

1. [API Core & System](#api-core--system)
2. [Data Query API](#data-query-api)
3. [Pupils API](#pupils-api)
4. [Families API](#families-api)
5. [Subjects & Classes API](#subjects--classes-api)
6. [Assessments & Reporting API](#assessments--reporting-api)
7. [Module-Specific APIs](#module-specific-apis)
   - [Medical Module](#medical-module)
   - [Leaves Module](#leaves-module)
   - [Absentees Module](#absentees-module)
   - [Applications Module](#applications-module)
   - [Records and Points Module](#records-and-points-module)
   - [Psychometric Module](#psychometric-module)
   - [Messaging Logs Module](#messaging-logs-module)
   - [Family Login Privileges Module](#family-login-privileges-module)
   - [DevMan Export Module](#devman-export-module)
8. [Staff API](#staff-api)
9. [Admissions API](#admissions-api)
10. [System Utilities APIs](#system-utilities-apis)
11. [API Authentication & Authorization](#api-authentication--authorization)
12. [API Response Format](#api-response-format)

---

## API Core & System

### GET `/api/request/test/{param1}/{param2}`
**File**: `classes/ADAM/API/Requests.php:157`
**Method**: `apiGetTest`

**Description**: Test endpoint for API connectivity and system information.

**Path Parameters**:
- `param1` (string, optional): Test parameter 1
- `param2` (string, optional): Test parameter 2

**Authorization**: None required

**Example Request**:
```bash
GET /api/request/test/hello/world
```

**Example Response**:
```json
{
  "data": {
    "parameter1": "hello",
    "parameter2": "world"
  },
  "message": "Hello, you're speaking to [School Name]. We are currently on revision [hash] and the local time is [time]."
}
```

---

### POST `/api/externalauth/auth`
**File**: `classes/ADAM/API/ExternalAuth.php:28`
**Method**: `apiPostAuth`

**Description**: Authenticate users (staff, pupils, or family members) via external authentication.

**Parameters** (POST body JSON):
- `username` (string, required): Username or ID number
- `password` (string, required): User password

**Authorization**: IP whitelist or API token required

**Example Request**:
```bash
POST /api/externalauth/auth
Content-Type: application/json

{
  "username": "jsmith",
  "password": "securepass123"
}
```

**Example Response** (Success):
```json
{
  "data": {
    "username": "jsmith",
    "firstname": "John",
    "lastname": "Smith",
    "email": "john.smith@example.com",
    "type": "staff",
    "id": 123
  },
  "response": {
    "code": 200,
    "error": "Login successful"
  }
}
```

**Example Response** (Failure):
```json
{
  "response": {
    "code": 401,
    "error": "Username or password not recognised"
  }
}
```

---

### GET `/api/admin/test`
**File**: `classes/ADAM/Support/Admin.php:325`

**Description**: Administrative test endpoint.

**Authorization**: Required

---

## Data Query API

### GET `/api/dataquery/get/{secret}/{version}`
**File**: `classes/ADAM/API/DataQuery.php:22`
**Method**: `apiGetGet`

**Description**: Retrieve data based on a predefined query configuration.

**Path Parameters**:
- `secret` (string, required): Query secret key
- `version` (int, optional, default: 1): API version (1 or 2)

**Authorization**: API token required

**Example Request**:
```bash
GET /api/dataquery/get/abc123/1
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 1,
      "pupil_firstname": "John",
      "pupil_lastname": "Doe"
    }
  ]
}
```

---

### GET `/api/dataquery/getone/{secret}/{identifier}/{version}`
**File**: `classes/ADAM/API/DataQuery.php:81`
**Method**: `apiGetGetOne`

**Description**: Retrieve data for a single individual based on a predefined query.

**Path Parameters**:
- `secret` (string, required): Query secret key
- `identifier` (int, required): Individual ID
- `version` (int, optional, default: 1): API version

**Authorization**: API token required

**Example Request**:
```bash
GET /api/dataquery/getone/abc123/42/1
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 42,
      "pupil_firstname": "Jane",
      "pupil_lastname": "Smith"
    }
  ]
}
```

---

### GET `/api/getsince/{secret}/{timestamp}/{version}`
**File**: `classes/ADAM/API/DataQuery.php:94`
**Method**: `apiGetGetSince`

**Description**: Retrieve records modified since a specific timestamp.

**Path Parameters**:
- `secret` (string, required): Query secret key
- `timestamp` (int, optional): Unix timestamp
- `version` (int, optional, default: 1): API version

**Authorization**: API token required

**Example Request**:
```bash
GET /api/getsince/abc123/1640995200/1
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_firstname": "Updated",
      "pupil_lastname": "Record"
    }
  ],
  "message": "Timestamp provided equates to 2022-01-01 00:00:00"
}
```

---

## Pupils API

### GET `/api/pupils/fields/{action}`
**File**: `classes/ADAM/Pupils/PupilsApi.php:34`
**Method**: `apiGetFields`

**Description**: Get field definitions for pupil table.

**Path Parameters**:
- `action` (string, optional): Field action type (add, edit, view)

**Authorization**: Required

**Example Request**:
```bash
GET /api/pupils/fields/add
```

**Example Response**:
```json
{
  "data": {
    "pupil_firstname": {
      "type": "text",
      "required": true,
      "editable": true
    },
    "pupil_lastname": {
      "type": "text",
      "required": true,
      "editable": true
    },
    "pupil_birth": {
      "type": "date",
      "required": false,
      "editable": true
    }
  }
}
```

---

### POST `/api/pupils/add`
**File**: `classes/ADAM/Pupils/PupilsApi.php:40`
**Method**: `apiPostAdd`

**Description**: Add a new pupil to the system.

**Parameters** (POST body JSON):
- Accepts any valid pupil field from the pupils table
- Common fields:
  - `pupil_firstname` (string, required)
  - `pupil_lastname` (string, required)
  - `pupil_birth` (date, optional)
  - `pupil_gender` (string, optional)
  - `pupil_idnumber` (string, optional)

**Authorization**: Required

**Example Request**:
```bash
POST /api/pupils/add
Content-Type: application/json

{
  "pupil_firstname": "Jane",
  "pupil_lastname": "Doe",
  "pupil_birth": "2010-05-15",
  "pupil_gender": "Female"
}
```

**Example Response**:
```json
{
  "data": 456
}
```
(Returns the new pupil ID)

---

### GET `/api/pupils/image/{pupil}/{width}`
**File**: `classes/ADAM/Pupils/PupilsApi.php:81`
**Method**: `apiGetImage`

**Description**: Get a pupil's photo/image.

**Path Parameters**:
- `pupil` (int, required): Pupil ID
- `width` (int, optional, default: 200): Image width in pixels

**Authorization**: Required

**Example Request**:
```bash
GET /api/pupils/image/123/300
```

**Response**: Binary image data (JPEG/PNG)

---

### GET `/api/pupils/pupil/{pupil}`
**File**: `classes/ADAM/Pupils/PupilsApi.php:99`
**Method**: `apiGetPupil`

**Description**: Get detailed information about a specific pupil.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/pupils/pupil/123
```

**Example Response**:
```json
{
  "data": {
    "pupil_id": 123,
    "pupil_firstname": "John",
    "pupil_lastname": "Doe",
    "pupil_grade": 10,
    "pupil_defaultclass": "10A Mathematics",
    "pupil_email": "john.doe@school.edu",
    "pupil_admin": "2024001",
    "pupil_birth": "2009-03-15",
    "pupil_gender": "Male"
  }
}
```

---

### GET `/api/pupils/contactlist`
**File**: `classes/ADAM/Pupils/PupilsApi.php:110`
**Method**: `apiGetContactList`

**Description**: Get a contact list of all pupils with basic information.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/pupils/contactlist
```

**Example Response**:
```json
{
  "data": [
    {
      "id": 123,
      "firstname": "John",
      "lastname": "Doe",
      "cell": "0821234567",
      "email": "john.doe@school.edu",
      "grade": 10
    },
    {
      "id": 124,
      "firstname": "Jane",
      "lastname": "Smith",
      "cell": "0829876543",
      "email": "jane.smith@school.edu",
      "grade": 11
    }
  ]
}
```

---

### GET `/api/pupils/searchbyid/{idNumber}`
**File**: `classes/ADAM/Pupils/PupilsApi.php:130`
**Method**: `searchByID`

**Description**: Search for pupils by ID number.

**Path Parameters**:
- `idNumber` (string, required): ID number to search

**Authorization**: Required

**Example Request**:
```bash
GET /api/pupils/searchbyid/0001010000001
```

**Example Response**:
```json
{
  "data": [123, 456]
}
```
(Returns array of matching pupil IDs)

---

## Families API

### GET `/api/families/fields/{action}`
**File**: `classes/ADAM/Families/Families.php:1920`
**Method**: `apiGetFields`

**Description**: Get field definitions for family table.

**Path Parameters**:
- `action` (string, optional): Field action type (add, edit, view)

**Authorization**: Required

**Example Request**:
```bash
GET /api/families/fields/add
```

**Example Response**:
```json
{
  "data": {
    "family_primary_firstname": {
      "type": "text",
      "required": true,
      "editable": true
    },
    "family_primary_lastname": {
      "type": "text",
      "required": true,
      "editable": true
    }
  }
}
```

---

### POST `/api/families/add`
**File**: `classes/ADAM/Families/Families.php:1930`
**Method**: `apiPostAdd`

**Description**: Add a new family to the system.

**Parameters** (POST body JSON):
- Accepts family table fields
- Common fields:
  - `family_primary_firstname` (string)
  - `family_primary_lastname` (string)
  - `family_primary_email` (string)

**Authorization**: Required

**Example Request**:
```bash
POST /api/families/add
Content-Type: application/json

{
  "family_primary_firstname": "John",
  "family_primary_lastname": "Smith",
  "family_primary_email": "john.smith@email.com"
}
```

**Example Response**:
```json
{
  "data": 789
}
```
(Returns the new family ID)

---

### POST `/api/families/link`
**File**: `classes/ADAM/Families/Families.php:1966`
**Method**: `apiPostLink`

**Description**: Link a pupil to a family.

**Parameters** (POST body JSON):
- `pupil` (int, required): Pupil ID
- `family` (int, required): Family ID
- `relationship` (string, required): Relationship type

**Authorization**: Required

**Example Request**:
```bash
POST /api/families/link
Content-Type: application/json

{
  "pupil": 123,
  "family": 789,
  "relationship": "child"
}
```

---

### POST `/api/families/email/{family}/{member}`
**File**: `classes/ADAM/Families/Families.php:80`
**Method**: `apiPostEmail`

**Description**: Add or update family email addresses.

**Path Parameters**:
- `family` (int, required): Family ID
- `member` (string, required): Family member (primary, secondary, etc.)

**Body Parameters**:
- `email` (string, required): Email address

**Authorization**: Required

**Example Request**:
```bash
POST /api/families/email/789/primary
Content-Type: application/x-www-form-urlencoded

email=newemail@example.com
```

---

### DELETE `/api/families/email/{family}/{member}`
**File**: `classes/ADAM/Families/Families.php:129`
**Method**: `apiDeleteEmail`

**Description**: Delete a family email address.

**Path Parameters**:
- `family` (int, required): Family ID
- `member` (string, required): Family member

**Body Parameters**:
- `email` (string, required): Email address to delete

**Authorization**: Required

**Example Request**:
```bash
DELETE /api/families/email/789/primary
Content-Type: application/x-www-form-urlencoded

email=old@example.com
```

---

### GET `/api/families/email/{family}/{member}`
**File**: `classes/ADAM/Families/Families.php:166`
**Method**: `apiGetEmail`

**Description**: Get family email addresses.

**Path Parameters**:
- `family` (int, required): Family ID
- `member` (string, optional): Specific family member

**Authorization**: Required

**Example Request**:
```bash
GET /api/families/email/789/primary
```

**Example Response**:
```json
{
  "data": ["john.smith@email.com", "john.smith2@email.com"]
}
```

---

### GET `/api/families/children/{family}`
**File**: `classes/ADAM/Families/Families.php:229`
**Method**: `apiGetChildren`

**Aliases**: `/api/families/get_children_by_family/{family}`

**Description**: Get children associated with a family.

**Path Parameters**:
- `family` (int, required): Family ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/families/children/789
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_firstname": "John",
      "pupil_lastname": "Smith",
      "pupil_admin": "2024001",
      "pupil_grade": 10,
      "relationship": "Child"
    },
    {
      "pupil_id": 124,
      "pupil_firstname": "Jane",
      "pupil_lastname": "Smith",
      "pupil_admin": "2024002",
      "pupil_grade": 8,
      "relationship": "Child"
    }
  ]
}
```

---

### GET `/api/families/currentchildren/{familyIdentifier}`
**File**: `classes/ADAM/Families/Families.php:943`
**Method**: `apiGetCurrentChildren`

**Description**: Get currently enrolled children for a family.

**Path Parameters**:
- `familyIdentifier` (int, required): Family ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/families/currentchildren/789
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_firstname": "John",
      "pupil_lastname": "Smith",
      "pupil_admin": "2024001",
      "pupil_final": "10"
    }
  ]
}
```

---

### GET `/api/families/detailsupdateform/{family}`
**File**: `classes/ADAM/Families/Families.php:398`
**Method**: `apiGetDetailsUpdateForm`

**Description**: Get a form for updating family details (typically for family portal).

**Path Parameters**:
- `family` (int, required): Family ID

**Authorization**: Requires `onlineupdate` privilege

**Example Request**:
```bash
GET /api/families/detailsupdateform/789
```

---

### GET `/api/families/searchbyid/{idNumber}`
**File**: `classes/ADAM/Families/Families.php:885`
**Method**: `apiGetSearchById`

**Description**: Search families by ID number.

**Path Parameters**:
- `idNumber` (string, required): ID number

**Authorization**: Required

**Example Request**:
```bash
GET /api/families/searchbyid/8001015678081
```

**Example Response**:
```json
{
  "data": 789
}
```
(Returns the family ID)

---

### GET `/api/families/contactlist`
**File**: `classes/ADAM/Families/Families.php:1727`
**Method**: `apiGetContactList`

**Description**: Get contact list of all families.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/families/contactlist
```

**Example Response**:
```json
{
  "data": [
    {
      "family_id": 789,
      "family_primary_firstname": "John",
      "family_primary_lastname": "Smith",
      "family_primary_email": "john.smith@email.com",
      "family_primary_cell": "0821234567"
    }
  ]
}
```

---

### GET `/api/families/familyrelationships`
**File**: `classes/ADAM/Families/Families.php:1836`
**Method**: `apiGetFamilyRelationships`

**Description**: Get family relationship types/definitions.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/families/familyrelationships
```

**Example Response**:
```json
{
  "data": [
    {
      "relationship_id": 1,
      "relationship_description": "Mother",
      "relationship_type": "parent"
    },
    {
      "relationship_id": 2,
      "relationship_description": "Father",
      "relationship_type": "parent"
    }
  ]
}
```

---

### GET `/api/familyrelationships/pupil/{pupil}`
**File**: `classes/ADAM/Families/FamilyRelationships.php:20`

**Description**: Get family relationships for a specific pupil.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/familyrelationships/pupil/123
```

**Example Response**:
```json
{
  "data": [
    {
      "family_id": 789,
      "relationship": "Mother",
      "family_primary_firstname": "Mary",
      "family_primary_lastname": "Smith"
    }
  ]
}
```

---

### GET `/api/familyrelationships/family/{family}`
**File**: `classes/ADAM/Families/FamilyRelationships.php:57`

**Description**: Get family relationship details for a family.

**Path Parameters**:
- `family` (int, required): Family ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/familyrelationships/family/789
```

---

## Subjects & Classes API

### GET `/api/subjects/get_by_grade/{grade}`
**File**: `classes/ADAM/Subjects/Subjects.php:289`
**Method**: `apiGetByGrade`

**Description**: Get subjects for a specific grade.

**Path Parameters**:
- `grade` (int, required): Grade level

**Authorization**: Privilege `promotions_edit` required

**Example Request**:
```bash
GET /api/subjects/get_by_grade/10
```

**Example Response**:
```json
{
  "data": [
    {
      "subject_id": 1,
      "subject_name": "Mathematics",
      "subject_short": "Math",
      "subject_sortorder": 1,
      "subject_category_id": 1,
      "category_description": "Core Subjects"
    },
    {
      "subject_id": 2,
      "subject_name": "English",
      "subject_short": "Eng",
      "subject_sortorder": 2,
      "subject_category_id": 1,
      "category_description": "Core Subjects"
    }
  ]
}
```

---

### GET `/api/subjects/get_by_grades/{gradeString}`
**File**: `classes/ADAM/Subjects/Subjects.php:213`
**Method**: `apiGetByGrades`

**Description**: Get subjects for multiple grades.

**Path Parameters**:
- `gradeString` (string, required): Comma-separated list of grades (e.g., "8,9,10")

**Authorization**: Privilege `promotions_edit` required

**Example Request**:
```bash
GET /api/subjects/get_by_grades/8,9,10
```

**Example Response**:
```json
{
  "data": [
    {
      "subject_id": 1,
      "subject_name": "Mathematics",
      "grade_id": 8
    },
    {
      "subject_id": 1,
      "subject_name": "Mathematics",
      "grade_id": 9
    }
  ]
}
```

---

### GET `/api/classes/pupilteachers/{pupil}`
**File**: `classes/ADAM/Classes/Classes.php:87`
**Method**: `apiGetPupilTeachers`

**Description**: Get teachers for a pupil's classes.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Requires `teachers` privilege (pupil-specific or family access)

**Example Request**:
```bash
GET /api/classes/pupilteachers/123
```

**Example Response**:
```json
{
  "data": [
    {
      "class_id": 45,
      "class_description": "10A",
      "class_gradeyear": 10,
      "subject_name": "Mathematics",
      "subject_short": "Math",
      "class_friendly": "Grade 10 10A",
      "staff": {
        "staff_id": 5,
        "staff_lastname": "Smith",
        "staff_firstname": "Jane",
        "staff_title": "Mrs",
        "staff_email": "jane.smith@school.edu"
      },
      "teaching_assistants": [
        {
          "staff_id": 6,
          "staff_lastname": "Jones",
          "staff_firstname": "Tom",
          "staff_title": "Mr",
          "staff_email": "tom.jones@school.edu"
        }
      ]
    }
  ]
}
```

---

### GET `/api/classes/bygradeperiodsubject/{grade}/{period}/{subject}`
**File**: `classes/ADAM/Classes/Classes.php:2190`

**Description**: Get classes by grade, period, and subject.

**Path Parameters**:
- `grade` (int, required): Grade level
- `period` (int, required): Reporting period ID
- `subject` (int, required): Subject ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/classes/bygradeperiodsubject/10/1/1
```

**Example Response**:
```json
{
  "data": [
    {
      "class_id": 45,
      "class_description": "10A Mathematics",
      "class_staff_id": 5,
      "class_gradeyear": 10
    }
  ]
}
```

---

### GET `/api/registrations/grade/{grade}`
**File**: `classes/ADAM/Classes/Registrations.php:813`
**Method**: `apiGetGrade`

**Description**: Get class registrations for a specific grade.

**Path Parameters**:
- `grade` (int, required): Grade level

**Authorization**: Required

**Example Request**:
```bash
GET /api/registrations/grade/10
```

**Example Response**:
```json
{
  "data": [
    {
      "registration_id": 1,
      "pupil_id": 123,
      "pupil_lastname": "Doe",
      "pupil_firstname": "John",
      "pupil_admin": "2024001",
      "class_id": 45,
      "class_description": "10A Mathematics",
      "class_gradeyear": 10,
      "subject_id": 1,
      "subject_name": "Mathematics",
      "subject_short": "Math",
      "category_id": 1,
      "category_description": "Academics",
      "registration_datestart": "2024-01-15",
      "registration_dateend": null,
      "staff_id": 5,
      "staff_firstname": "Jane",
      "staff_lastname": "Smith"
    }
  ]
}
```

---

## Assessments & Reporting API

### GET `/api/assessment/recentresults/{pupil}`
**File**: `classes/ADAM/Assessments/AssessmentHelper.php:1479`
**Method**: `apiGetRecentAssessmentResults`

**Description**: Get recent assessment results for a pupil.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Requires `marks` privilege (pupil-specific or family access)

**Example Request**:
```bash
GET /api/assessment/recentresults/123
```

**Example Response**:
```json
{
  "data": [
    {
      "assessment_id": 456,
      "assessment_period_id": 1,
      "assessment_description": "Term Test",
      "assessment_date": "2024-03-15",
      "assessment_releasedate": "2024-03-20",
      "assessment_total": 100,
      "assessment_weighting": 50.0,
      "result_total": 85,
      "result_comment": "Well done!",
      "class_grade_id": 10,
      "class_description": "10A Mathematics",
      "subject_id": 1,
      "subject_name": "Mathematics",
      "subject_short": "Math"
    }
  ]
}
```

---

### GET `/api/questions/questionbreakdown/{assessment}`
**File**: `classes/ADAM/Assessments/Questions.php:377`

**Description**: Get question breakdown/statistics for an assessment.

**Path Parameters**:
- `assessment` (int, required): Assessment ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/questions/questionbreakdown/456
```

**Example Response**:
```json
{
  "data": [
    {
      "question_number": 1,
      "question_marks": 5,
      "average_score": 4.2,
      "pass_rate": 85.5
    }
  ]
}
```

---

### GET `/api/reporting/pupilreportingperiods/{pupil}`
**File**: `classes/ADAM/Reporting/Reporting.php:87`
**Method**: `apiGetPupilReportingPeriods`

**Description**: Get reporting periods available for a pupil.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Requires one of: `marks`, `closedmarks`, `reports`, `closeouts` privileges

**Example Request**:
```bash
GET /api/reporting/pupilreportingperiods/123
```

**Example Response**:
```json
{
  "data": [
    {
      "period_id": 1,
      "period_name": "Term 1 2024",
      "period_start": "2024-01-15",
      "period_end": "2024-03-31",
      "period_publish": "2024-04-05",
      "report_aggregate": 75.5,
      "report_aggregate_ytd": 75.5,
      "document_id": 123,
      "document_upload_date": "2024-04-05",
      "pupil_gradetext": "Grade 10"
    }
  ]
}
```

---

### GET `/api/reporting/periods/{year}`
**File**: `classes/ADAM/Reporting/Reporting.php:114`
**Method**: `apiGetPeriods`

**Description**: Get all reporting periods for a specific year.

**Path Parameters**:
- `year` (int, optional): Year (defaults to current year)

**Authorization**: Required

**Example Request**:
```bash
GET /api/reporting/periods/2024
```

**Example Response**:
```json
{
  "data": [
    {
      "period_id": 1,
      "period_name": "Term 1 2024",
      "period_start": "2024-01-15",
      "period_end": "2024-03-31",
      "period_publish": "2024-04-05"
    },
    {
      "period_id": 2,
      "period_name": "Term 2 2024",
      "period_start": "2024-04-15",
      "period_end": "2024-06-30",
      "period_publish": "2024-07-05"
    }
  ],
  "message": "Reporting periods from year 2024"
}
```

---

### GET `/api/reporting/results/{period}`
**File**: `classes/ADAM/Reporting/Reporting.php:130`
**Method**: `apiGetResults`

**Description**: Get reporting results for all pupils in a period.

**Path Parameters**:
- `period` (int, required): Reporting period ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/reporting/results/1
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_admin": "2024001",
      "pupil_grade": 10,
      "results": [
        {
          "subject_id": 1,
          "subject_name": "Mathematics",
          "dbe_subject_code": "MATH",
          "result_term": 85,
          "result_ytd": 82
        }
      ],
      "report_aggregate": 75.5,
      "report_aggregate_ytd": 74.2,
      "report_modified": "2024-04-05 14:30:00"
    }
  ]
}
```

---

### GET `/api/reporting/subjectmarksbypupil/{pupil}`
**File**: `classes/ADAM/Reporting/Reporting.php:174`
**Method**: `apiGetSubjectMarksByPupil`

**Description**: Get subject marks for a specific pupil across all periods.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Requires `marks` privilege

**Example Request**:
```bash
GET /api/reporting/subjectmarksbypupil/123
```

**Example Response**:
```json
{
  "data": [
    {
      "period_id": 1,
      "period_name": "Term 1 2024",
      "period_date": "2024-03-31",
      "subjects": [
        {
          "subject_id": 1,
          "grade": 10,
          "subject_name": "Mathematics",
          "subject_short": "Math",
          "teacher_email": "jane.smith@school.edu",
          "teacher_name": "Mrs Jane Smith",
          "result": 85,
          "class_friendly": "Grade 10 10A"
        }
      ]
    }
  ]
}
```

---

### GET `/api/reporting/markbook/{period}/{pupil}`
**File**: `classes/ADAM/Reporting/Reporting.php:216`
**Method**: `apiGetMarkBook`

**Description**: Get detailed markbook/assessment data for a pupil in a period.

**Path Parameters**:
- `period` (int, required): Reporting period ID
- `pupil` (int, required): Pupil ID

**Authorization**: Requires `marks` (current period) or `closedmarks` (past period)

**Example Request**:
```bash
GET /api/reporting/markbook/1/123
```

**Example Response**:
```json
{
  "data": [
    {
      "subject_name": "Mathematics",
      "subject_short": "Math",
      "class_teacher": "Mrs Jane Smith",
      "class_gradeyear": 10,
      "class_description": "10A",
      "class_friendly": "Mathematics: Grade 10 10A",
      "assessment_categories": [
        {
          "category_description": "Tests",
          "assessments": [
            {
              "result_total": 85,
              "result_comment": "Well done!",
              "assessment_description": "Term Test",
              "assessment_date": "2024-03-15",
              "assessment_releasedate": "2024-03-20",
              "assessment_total": 100
            }
          ]
        }
      ]
    }
  ]
}
```

---

### GET `/api/reporting/report/{period}/{pupil}`
**File**: `classes/ADAM/Reporting/Reporting.php:276`
**Method**: `apiGetReport`

**Description**: Get a pupil's report document (PDF).

**Path Parameters**:
- `period` (int, required): Reporting period ID
- `pupil` (int, required): Pupil ID

**Authorization**: Requires `reports` (current) or `closedreports` (past)

**Example Request**:
```bash
GET /api/reporting/report/1/123
```

**Response**: Binary PDF data

---

### GET `/api/reporting/previousreports/{pupil}`
**File**: `classes/ADAM/Reporting/Reporting.php:2521`

**Description**: Get list of previous reports for a pupil.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/reporting/previousreports/123
```

**Example Response**:
```json
{
  "data": [
    {
      "period_id": 1,
      "period_name": "Term 1 2024",
      "document_id": 456,
      "document_upload_date": "2024-04-05"
    }
  ]
}
```

---

## Module-Specific APIs

### Medical Module

#### GET `/api/medical/offsport/{date}`
**File**: `classes/ADAM/Modules/Medical/Medical.php:240`
**Method**: `apiGetOffSport`

**Description**: Get the off-sport list for a specific date (pupils who cannot participate in sports activities).

**Path Parameters**:
- `date` (string, optional): Date in YYYY-MM-DD format (defaults to today)

**Authorization**: Required

**Example Request**:
```bash
GET /api/medical/offsport/2024-03-15
```

**Example Response**:
```json
{
  "data": [123, 456, 789],
  "message": "Offsport list for 2024-03-15."
}
```
(Returns array of pupil IDs who are off sport on that date)

---

### Leaves Module

#### GET `/api/leaves/approved/{from}/{to}`
**File**: `classes/ADAM/Modules/Leaves/Leaves.php:942`

**Description**: Get approved leave requests.

**Path Parameters**:
- `from` (string, optional): Start date (YYYY-MM-DD)
- `to` (string, optional): End date (YYYY-MM-DD)

**Authorization**: Required

**Example Request**:
```bash
GET /api/leaves/approved/2024-03-01/2024-03-31
```

**Example Response**:
```json
{
  "data": [
    {
      "leave_id": 1,
      "pupil_id": 123,
      "leave_start": "2024-03-15",
      "leave_end": "2024-03-20",
      "leave_reason": "Family vacation"
    }
  ]
}
```

---

### Absentees Module

#### GET `/api/absentees/daysabsentforpupil/{pupil}/{year}`
**File**: `classes/ADAM/Modules/Absentees/Absentees.php:312`
**Method**: `apiGetDaysAbsentForPupil`

**Description**: Get number of days absent for a pupil.

**Path Parameters**:
- `pupil` (int, required): Pupil ID
- `year` (int, optional): Specific year to filter by

**Authorization**: Requires `absentee` privilege

**Example Request**:
```bash
GET /api/absentees/daysabsentforpupil/123/2024
```

**Example Response**:
```json
{
  "data": [
    {
      "absent_date": "2024-03-15",
      "reason_description": "Illness",
      "absent_notes": "Flu"
    },
    {
      "absent_date": "2024-03-16",
      "reason_description": "Illness",
      "absent_notes": "Flu"
    }
  ]
}
```

---

#### GET `/api/absentees/summarycount/{from}/{to}`
**File**: `classes/ADAM/Modules/Absentees/Absentees.php:335`
**Method**: `apiGetSummaryCount`

**Description**: Get summary count of absentees for all pupils in a date range.

**Path Parameters**:
- `from` (string, required): Start date (YYYY-MM-DD)
- `to` (string, optional): End date (defaults to today)

**Authorization**: Required

**Example Request**:
```bash
GET /api/absentees/summarycount/2024-01-01/2024-03-31
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_admin": "2024001",
      "absent_count": 5
    },
    {
      "pupil_id": 124,
      "pupil_admin": "2024002",
      "absent_count": 2
    }
  ],
  "message": "Absentee counts for all pupils from 2024-01-01 to 2024-03-31."
}
```

---

#### GET `/api/absentees/list/{from}/{to}`
**File**: `classes/ADAM/Modules/Absentees/Absentees.php:376`
**Method**: `apiGetList`

**Description**: Get detailed list of absentees for a date range.

**Path Parameters**:
- `from` (string, optional): Start date (defaults to today)
- `to` (string, optional): End date (defaults to `from` date)

**Authorization**: Required

**Example Request**:
```bash
GET /api/absentees/list/2024-03-15/2024-03-16
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_admin": "2024001",
      "absent_date": "2024-03-15",
      "absent_reason_id": 1,
      "absent_reason_description": "Illness",
      "absent_notes": "Flu"
    }
  ],
  "message": "Absentee list for all pupils from 2024-03-15 to 2024-03-16."
}
```

---

#### POST `/api/absenteekiosk/register/{pupil}`
**File**: `classes/ADAM/Modules/Absentees/AbsenteesKioskController.php:30`
**Method**: `apiPostRegister`

**Description**: Register a pupil's attendance via an absentee kiosk (typically used for morning registration).

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Requires `absentee-rapid` privilege (Staff API Access)

**Example Request**:
```bash
POST /api/absenteekiosk/register/123
```

**Example Response** (Present):
```json
{
  "data": {
    "message": "<strong>John Doe</strong> was registered as <strong>Present</strong>",
    "colour": "green"
  },
  "response": {
    "code": 200,
    "error": "Present"
  }
}
```

**Example Response** (Late):
```json
{
  "data": {
    "message": "<strong>John Doe</strong> was registered as <strong>Late</strong>",
    "colour": "#efa300"
  },
  "response": {
    "code": 202,
    "error": "Late"
  }
}
```

**Example Response** (Not in time window):
```json
{
  "data": {
    "message": "<strong>John Doe</strong> was NOT registered.",
    "colour": "#ff5050"
  },
  "response": {
    "code": 406
  }
}
```

---

### Applications Module

#### GET `/api/applications/verifyid/{idNumber}`
**File**: `classes/ADAM/Modules/Applications/ApplicationsApi.php:25`

**Description**: Verify an ID number for application (checks if ID is valid and not already in system).

**Path Parameters**:
- `idNumber` (string, required): ID number to verify

**Authorization**: Required

**Example Request**:
```bash
GET /api/applications/verifyid/0505155678081
```

**Example Response** (Valid):
```json
{
  "data": {
    "valid": true,
    "exists": false
  }
}
```

**Example Response** (Already exists):
```json
{
  "data": {
    "valid": true,
    "exists": true,
    "pupil_id": 123
  }
}
```

---

#### POST `/api/applications/apply`
**File**: `classes/ADAM/Modules/Applications/ApplicationsApi.php:51`

**Description**: Submit a new application for admission.

**Parameters** (POST body JSON):
- Application form data (varies based on form configuration)
- Common fields:
  - `pupil_firstname` (string)
  - `pupil_lastname` (string)
  - `pupil_birth` (date)
  - `family_*` fields for family information

**Authorization**: May require token or be publicly accessible depending on configuration

**Example Request**:
```bash
POST /api/applications/apply
Content-Type: application/json

{
  "pupil_firstname": "John",
  "pupil_lastname": "Doe",
  "pupil_birth": "2010-05-15",
  "family_primary_firstname": "Jane",
  "family_primary_lastname": "Doe",
  "family_primary_email": "jane.doe@email.com"
}
```

**Example Response**:
```json
{
  "data": {
    "application_id": 456,
    "pupil_id": 789
  },
  "message": "Application submitted successfully"
}
```

---

#### GET `/api/applications/applicationformfields`
**File**: `classes/ADAM/Modules/Applications/ApplicationsApi.php:130`

**Description**: Get application form field definitions.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/applications/applicationformfields
```

**Example Response**:
```json
{
  "data": {
    "pupil_fields": [
      {
        "field_name": "pupil_firstname",
        "field_type": "text",
        "required": true,
        "label": "First Name"
      }
    ],
    "family_fields": [
      {
        "field_name": "family_primary_email",
        "field_type": "email",
        "required": true,
        "label": "Primary Email"
      }
    ]
  }
}
```

---

### Records and Points Module

#### GET `/api/recordsandpoints/recentpupilrecords/{pupil}`
**File**: `classes/ADAM/Modules/RecordsAndPoints/RecordsAndPoints.php:975`

**Description**: Get recent records (achievements/disciplinary) for a pupil.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/recordsandpoints/recentpupilrecords/123
```

**Example Response**:
```json
{
  "data": [
    {
      "record_id": 1,
      "record_date": "2024-03-15",
      "record_type": "Achievement",
      "record_description": "Excellent performance in Math",
      "record_points": 5
    }
  ]
}
```

---

#### GET `/api/recordsandpoints/pupilrecords/{pupil}/{from}/{to}`
**File**: `classes/ADAM/Modules/RecordsAndPoints/RecordsAndPoints.php:1030`

**Description**: Get all records for a pupil (with date range filtering).

**Path Parameters**:
- `pupil` (int, required): Pupil ID
- `from` (string, optional): Start date
- `to` (string, optional): End date

**Authorization**: Required

**Example Request**:
```bash
GET /api/recordsandpoints/pupilrecords/123/2024-01-01/2024-03-31
```

**Example Response**:
```json
{
  "data": [
    {
      "record_id": 1,
      "record_date": "2024-03-15",
      "record_type": "Achievement",
      "record_description": "Excellent performance in Math",
      "record_points": 5,
      "staff_name": "Mrs Smith"
    },
    {
      "record_id": 2,
      "record_date": "2024-02-10",
      "record_type": "Disciplinary",
      "record_description": "Late to class",
      "record_points": -2,
      "staff_name": "Mr Jones"
    }
  ]
}
```

---

### Psychometric Module

#### GET `/api/psychometric/assessmentsbycategory/{pupil}/{category}`
**File**: `classes/ADAM/Modules/Psychometric/Psychometric.php:306`

**Aliases**: `/api/psychometric/assessments_by_category/{pupil}/{category}`

**Description**: Get psychometric assessments organized by category.

**Path Parameters**:
- `pupil` (int, optional): Specific pupil ID
- `category` (int, optional): Specific category ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/psychometric/assessmentsbycategory/123
```

**Example Response**:
```json
{
  "data": [
    {
      "category_name": "Cognitive Assessments",
      "assessments": [
        {
          "assessment_id": 1,
          "assessment_name": "IQ Test",
          "assessment_date": "2024-01-15",
          "score": 125
        }
      ]
    }
  ]
}
```

---

### Messaging Logs Module

#### GET `/api/messaginglogs/messages/{from}/{to}`
**File**: `classes/ADAM/Modules/MessagingLogs/MessagingLogs.php:76`

**Description**: Get messaging logs (sent messages).

**Path Parameters**:
- `from` (string, optional): Start date
- `to` (string, optional): End date

**Authorization**: Required

**Example Request**:
```bash
GET /api/messaginglogs/messages/2024-03-01/2024-03-31
```

**Example Response**:
```json
{
  "data": [
    {
      "message_id": 1,
      "message_subject": "School Event",
      "message_date": "2024-03-15",
      "message_type": "Email",
      "recipients_count": 150
    }
  ]
}
```

---

#### GET `/api/messaginglogs/message/{message}`
**File**: `classes/ADAM/Modules/MessagingLogs/MessagingLogs.php:89`

**Description**: Get details of a specific message.

**Path Parameters**:
- `message` (int, required): Message ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/messaginglogs/message/1
```

**Example Response**:
```json
{
  "data": {
    "message_id": 1,
    "message_subject": "School Event",
    "message_body": "Dear Parents...",
    "message_date": "2024-03-15",
    "message_type": "Email",
    "recipients": [
      {
        "recipient_email": "parent1@email.com",
        "status": "Sent"
      }
    ]
  }
}
```

---

#### GET `/api/messaginglogs/messagebyid/{id}`
**File**: `classes/ADAM/Modules/MessagingLogs/MessagingLogs.php:106`

**Description**: Get a message by its unique identifier (alternative to `/message`).

**Path Parameters**:
- `id` (int, required): Message ID

**Authorization**: Required

---

### Family Login Privileges Module

#### GET `/api/familylogin/privileges/{family}`
**File**: `classes/ADAM/Modules/FamilyLoginPrivileges/FamilyLoginPrivileges.php:436`

**Description**: Get family login privileges for a family account.

**Path Parameters**:
- `family` (int, required): Family ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/familylogin/privileges/789
```

**Example Response**:
```json
{
  "data": {
    "marks": true,
    "reports": true,
    "absentee": true,
    "financial": false
  }
}
```

---

### DevMan Export Module

These endpoints are specifically for exporting data to the DevMan (Development Management) system.

#### GET `/api/xdevman/alumni`
**File**: `classes/ADAM/Modules/DevManExport/DevManExport.php:24`

**Description**: Export alumni (past pupils) data for DevMan.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/xdevman/alumni
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_firstname": "John",
      "pupil_lastname": "Doe",
      "pupil_admin": "2020001",
      "year_left": 2020
    }
  ]
}
```

---

#### GET `/api/xdevman/leavers`
**File**: `classes/ADAM/Modules/DevManExport/DevManExport.php:32`

**Description**: Export recent leavers data for DevMan.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/xdevman/leavers
```

---

#### GET `/api/xdevman/currentpupils`
**File**: `classes/ADAM/Modules/DevManExport/DevManExport.php:40`

**Description**: Export current pupils data for DevMan.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/xdevman/currentpupils
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_firstname": "Jane",
      "pupil_lastname": "Smith",
      "pupil_admin": "2024001",
      "pupil_grade": 10
    }
  ]
}
```

---

#### GET `/api/xdevman/alumnus/{pupil}`
**File**: `classes/ADAM/Modules/DevManExport/DevManExport.php:48`

**Description**: Export single alumnus data for DevMan.

**Path Parameters**:
- `pupil` (int, required): Pupil ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/xdevman/alumnus/123
```

---

## Staff API

### GET `/api/staff/image/{staff}/{width}`
**File**: `classes/ADAM/Staff/Staff.php:424`

**Description**: Get a staff member's photo/image.

**Path Parameters**:
- `staff` (int, required): Staff ID
- `width` (int, optional): Image width in pixels

**Authorization**: Required

**Example Request**:
```bash
GET /api/staff/image/5/200
```

**Response**: Binary image data (JPEG/PNG)

---

## Admissions API

### GET `/api/registration/statuslist`
**File**: `classes/ADAM/Admissions/Registration.php:1461`

**Description**: Get list of registration statuses available in the system.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/registration/statuslist
```

**Example Response**:
```json
{
  "data": [
    {
      "status_id": 1,
      "status_description": "Applied",
      "status_stage": "pre"
    },
    {
      "status_id": 2,
      "status_description": "Accepted",
      "status_stage": "pre"
    },
    {
      "status_id": 3,
      "status_description": "Enrolled",
      "status_stage": "current"
    }
  ]
}
```

---

### GET `/api/registration/statuses`
**File**: `classes/ADAM/Admissions/Registration.php:1585`

**Description**: Get all pupil registration statuses.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/registration/statuses
```

**Example Response**:
```json
{
  "data": [
    {
      "pupil_id": 123,
      "pupil_admin": "2024001",
      "status_id": 3,
      "status_description": "Enrolled",
      "status_date": "2024-01-15"
    }
  ]
}
```

---

### POST `/api/registration/status`
**File**: `classes/ADAM/Admissions/Registration.php:1595`

**Description**: Update a pupil's registration status.

**Parameters** (POST body JSON):
- `pupil` (int, required): Pupil ID
- `status` (int, required): New status ID
- `date` (string, optional): Effective date

**Authorization**: Required

**Example Request**:
```bash
POST /api/registration/status
Content-Type: application/json

{
  "pupil": 123,
  "status": 3,
  "date": "2024-01-15"
}
```

**Example Response**:
```json
{
  "message": "Status updated successfully"
}
```

---

## System Utilities APIs

### GET `/api/cron/cronlog/{limit}`
**File**: `classes/ADAM/Support/Cron/Cron.php:117`

**Description**: Get cron job execution logs.

**Path Parameters**:
- `limit` (int, optional): Number of log entries to return

**Authorization**: Required

**Example Request**:
```bash
GET /api/cron/cronlog/50
```

**Example Response**:
```json
{
  "data": [
    {
      "log_id": 1,
      "job_name": "DailyBackup",
      "execution_time": "2024-03-15 02:00:00",
      "status": "Success",
      "duration": 120
    }
  ]
}
```

---

### POST `/api/changelog/undo/{change}`
**File**: `classes/ADAM/Support/ChangeLog.php:278`

**Description**: Undo a changelog entry (revert a change).

**Path Parameters**:
- `change` (int, required): Change log ID

**Authorization**: Required

**Example Request**:
```bash
POST /api/changelog/undo/123
```

**Example Response**:
```json
{
  "message": "Change undone successfully"
}
```

---

### GET `/api/migration/version`
**File**: `classes/ADAM/Support/Migration.php:108`

**Description**: Get migration/export version information.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/migration/version
```

**Example Response**:
```json
{
  "data": {
    "version": "3.2.1",
    "database_version": "2024.03.15"
  }
}
```

---

### GET `/api/migration/tablelist`
**File**: `classes/ADAM/Support/Migration.php:115`

**Description**: Get list of database tables available for migration/export.

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/migration/tablelist
```

**Example Response**:
```json
{
  "data": [
    "pupils",
    "families",
    "staff",
    "classes"
  ]
}
```

---

### GET `/api/migration/tablerows/{table}`
**File**: `classes/ADAM/Support/Migration.php:130`

**Description**: Get row count information for migration tables.

**Path Parameters**:
- `table` (string, required): Table name

**Authorization**: Required

**Example Request**:
```bash
GET /api/migration/tablerows/pupils
```

**Example Response**:
```json
{
  "data": {
    "table": "pupils",
    "row_count": 1250
  }
}
```

---

### GET `/api/migration/tabledata/{table}/{offset}/{limit}`
**File**: `classes/ADAM/Support/Migration.php:142`

**Description**: Get table data for migration/export.

**Path Parameters**:
- `table` (string, required): Table name
- `offset` (int, optional): Starting offset
- `limit` (int, optional): Number of rows

**Authorization**: Required

**Example Request**:
```bash
GET /api/migration/tabledata/pupils/0/100
```

---

### GET `/api/migration/docrepfile/{document}`
**File**: `classes/ADAM/Support/Migration.php:152`

**Description**: Get document repository file for migration.

**Path Parameters**:
- `document` (int, required): Document ID

**Authorization**: Required

**Example Request**:
```bash
GET /api/migration/docrepfile/456
```

**Response**: Binary file data

---

### GET `/api/tablefields/fields/{table}/{action}`
**File**: `classes/ADAM/Support/TableFields.php:128`

**Description**: Get table field definitions for any database table.

**Path Parameters**:
- `table` (string, required): Table name constant (e.g., "pupils", "families")
- `action` (string, optional): Action type (add, edit, view)

**Authorization**: Required

**Example Request**:
```bash
GET /api/tablefields/fields/pupils/edit
```

**Example Response**:
```json
{
  "data": {
    "pupil_firstname": {
      "type": "text",
      "required": true,
      "editable": true,
      "max_length": 100
    }
  }
}
```

---

### GET `/api/formfields/fields/{form}`
**File**: `classes/ADAM/Support/FormFields.php:144`

**Description**: Get form field definitions (for dynamic forms).

**Path Parameters**:
- `form` (string, required): Form identifier

**Authorization**: Required

**Example Request**:
```bash
GET /api/formfields/fields/application
```

**Example Response**:
```json
{
  "data": [
    {
      "field_id": 1,
      "field_name": "preferred_name",
      "field_type": "text",
      "field_label": "Preferred Name",
      "required": false
    }
  ]
}
```

---

### GET `/api/export/families`
**File**: `classes/ADAM/Integrations/Export.php:18`

**Description**: Export family data (for integrations).

**Path Parameters**: None

**Authorization**: Required

**Example Request**:
```bash
GET /api/export/families
```

**Example Response**:
```json
{
  "data": [
    {
      "family_id": 789,
      "family_primary_firstname": "John",
      "family_primary_lastname": "Smith",
      "children": [123, 124]
    }
  ]
}
```

---

## API Authentication & Authorization

### Token-Based Authentication

Most API endpoints require an API token to be included in the request. The token should be passed in the Authorization header:

**Recommended Method** (Authorization Header):
```bash
Authorization: Bearer YOUR_API_TOKEN
```

### IP Whitelisting

The External Authentication endpoint (`/api/externalauth/auth`) supports IP whitelisting as configured in the system settings (`extauth_ip`). This allows certain IP addresses to access the endpoint without token authentication.

### Privilege Checks

Many endpoints perform privilege checks using:

- **`Privileges` class**: Checks if the authenticated user has specific privileges
- **`#[StaffApiAccess]` attribute**: Limits endpoint access to staff with specific privileges
- **Pupil/Family-specific access**: Some endpoints check if the authenticated user has access to specific pupil or family data

### Common Authorization Patterns

1. **Staff-only endpoints**: Require staff authentication and specific privileges
2. **Pupil portal endpoints**: Accessible by pupils or their families with appropriate privileges
3. **Public endpoints**: Limited to application forms and external authentication

---

## API Response Format

All API responses follow a standard format:

```json
{
  "data": {},
  "message": "",
  "response": {
    "code": 200,
    "error": ""
  }
}
```

### Success Response Example
```json
{
  "data": {
    "pupil_id": 123,
    "pupil_firstname": "John",
    "pupil_lastname": "Doe"
  },
  "message": "Pupil retrieved successfully",
  "response": {
    "code": 200
  }
}
```

### Error Response Example
```json
{
  "response": {
    "code": 400,
    "error": "Invalid pupil ID provided"
  }
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 202 | Accepted | Request accepted (e.g., late registration) |
| 400 | Bad Request | Invalid parameters or malformed request |
| 401 | Unauthorized | Authentication failed or missing |
| 403 | Forbidden | Insufficient privileges |
| 404 | Not Found | Resource not found |
| 406 | Not Acceptable | Request cannot be processed (e.g., outside time window) |
| 500 | Internal Server Error | Server-side error |

---

## General Notes

### Date and Time Formats

- **Dates**: ISO 8601 format `YYYY-MM-DD` (e.g., "2024-03-15")
- **Timestamps**: Unix timestamp (seconds since epoch) or ISO datetime format
- **Timezone**: Server timezone (typically configured in settings)

### Path Parameter Format

**IMPORTANT**: Parameters are passed in the URL path, separated by `/`, NOT as query parameters.

**Correct**:
```bash
GET /api/pupils/pupil/123
GET /api/families/children/789
GET /api/reporting/markbook/1/123
```

**Incorrect** (DO NOT USE):
```bash
GET /api/pupils/pupil?pupil=123
GET /api/families/children?family=789
GET /api/reporting/markbook?period=1&pupil=123
```

### Binary Responses

Some endpoints (images, PDFs) return binary data:
- **Content-Type** header indicates the file type (e.g., `image/jpeg`, `application/pdf`)
- No JSON wrapping for binary responses

### Pagination

- Most endpoints do NOT implement pagination
- Large result sets are returned in full
- Consider filtering by date range or other path parameters to limit results

### Rate Limiting

- Not implemented at the application level
- Should be implemented at infrastructure level (web server, API gateway)

### API Versioning

Some endpoints support a `version` path parameter:
- `version=1`: Returns associative array format (default)
- `version=2`: Returns indexed array format

### Data Filtering

Many endpoints support filter parameters as part of the path:
- Date ranges: `/from/to` path parameters
- Specific years: `/year` path parameter
- Resource IDs: `/pupil`, `/family`, `/staff`, etc.

### Field Visibility

- Sensitive fields are filtered based on user privileges
- Different filter levels: `FILTER_PUPIL_STANDARD`, `FILTER_FAMILY_STANDARD`, etc.
- API responses typically exclude internal/system fields

### Error Handling

- Validation errors return 400 with descriptive error message
- Authorization errors return 401 or 403
- Database errors are caught and logged server-side
- Client receives generic 500 error for unhandled exceptions

---

## Integration Examples

### Example 1: Get Pupil Information
```bash
curl -X GET "https://school.adam.co.za/api/pupils/pupil/123" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

**Response**:
```json
{
  "data": {
    "pupil_id": 123,
    "pupil_firstname": "John",
    "pupil_lastname": "Doe",
    "pupil_admin": "2024001",
    "pupil_grade": 10
  }
}
```

### Example 2: Submit Application
```bash
curl -X POST "https://school.adam.co.za/api/applications/apply" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pupil_firstname": "Jane",
    "pupil_lastname": "Smith",
    "pupil_birth": "2010-05-15",
    "family_primary_email": "jane.smith@email.com"
  }'
```

**Response**:
```json
{
  "data": {
    "application_id": 456,
    "pupil_id": 789
  },
  "message": "Application submitted successfully"
}
```

### Example 3: Get Assessment Results
```bash
curl -X GET "https://school.adam.co.za/api/assessment/recentresults/123" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

**Response**:
```json
{
  "data": [
    {
      "assessment_description": "Term Test",
      "assessment_date": "2024-03-15",
      "assessment_total": 100,
      "result_total": 85,
      "subject_name": "Mathematics"
    }
  ]
}
```

### Example 4: Get Multiple Path Parameters
```bash
curl -X GET "https://school.adam.co.za/api/reporting/markbook/1/123" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

This retrieves the markbook for period ID 1 and pupil ID 123.

---

## Additional Resources

- **API Configuration**: `/admin/api` in the ADAM interface
- **API Token Management**: `/admin/api/tokens`
- **Data Query Builder**: `/admin/dataquery` for creating custom queries
- **Privilege Management**: `/admin/privileges` for configuring access control

---

## Support and Contact

For API support and questions:
- Review the implementation files listed in each endpoint's documentation
- Check system logs at `temp/logs/` for error details
- Contact ADAM support: philip@adam.co.za

---

**Document Version**: 1.1
**Last Updated**: 2025-03-01
**ADAM Version**: 3.x+
