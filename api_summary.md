  API Core & System

  | Endpoint                            | Method | Returns                                                                      |
  |-------------------------------------|--------|------------------------------------------------------------------------------|
  | /api/request/test/{param1}/{param2} | GET    | System information, revision hash, local time, and test parameters           |
  | /api/externalauth/auth              | POST   | User authentication details (username, firstname, lastname, email, type, id) |
  | /api/admin/test                     | GET    | Administrative test response                                                 |

  Data Query API

  | Endpoint                                              | Method | Returns                                                |
  |-------------------------------------------------------|--------|--------------------------------------------------------|
  | /api/dataquery/get/{secret}/{version}                 | GET    | Custom query results based on predefined configuration |
  | /api/dataquery/getone/{secret}/{identifier}/{version} | GET    | Single individual's data based on predefined query     |
  | /api/getsince/{secret}/{timestamp}/{version}          | GET    | Records modified since specified timestamp             |

  Pupils API

  | Endpoint                          | Method | Returns                                                                           |
  |-----------------------------------|--------|-----------------------------------------------------------------------------------|
  | /api/pupils/fields/{action}       | GET    | Field definitions for pupil table (type, required, editable)                      |
  | /api/pupils/add                   | POST   | New pupil ID                                                                      |
  | /api/pupils/image/{pupil}/{width} | GET    | Pupil photo (binary JPEG/PNG)                                                     |
  | /api/pupils/pupil/{pupil}         | GET    | Complete pupil information (name, grade, admin number, email, birth date, gender) |
  | /api/pupils/contactlist           | GET    | All pupils with basic contact info (id, name, cell, email, grade)                 |
  | /api/pupils/searchbyid/{idNumber} | GET    | Array of pupil IDs matching the ID number                                         |

  Families API

  | Endpoint                                         | Method | Returns                                                        |
  |--------------------------------------------------|--------|----------------------------------------------------------------|
  | /api/families/fields/{action}                    | GET    | Field definitions for family table                             |
  | /api/families/add                                | POST   | New family ID                                                  |
  | /api/families/link                               | POST   | Confirmation of pupil-family link                              |
  | /api/families/email/{family}/{member}            | POST   | Email addition confirmation                                    |
  | /api/families/email/{family}/{member}            | DELETE | Email deletion confirmation                                    |
  | /api/families/email/{family}/{member}            | GET    | Array of email addresses for family member                     |
  | /api/families/children/{family}                  | GET    | Children linked to family (pupil details, grade, relationship) |
  | /api/families/currentchildren/{familyIdentifier} | GET    | Currently enrolled children for family                         |
  | /api/families/detailsupdateform/{family}         | GET    | Form for updating family details                               |
  | /api/families/searchbyid/{idNumber}              | GET    | Family ID matching the ID number                               |
  | /api/families/contactlist                        | GET    | All families with contact information                          |
  | /api/families/familyrelationships                | GET    | Family relationship types/definitions                          |
  | /api/familyrelationships/pupil/{pupil}           | GET    | Family relationships for specific pupil                        |
  | /api/familyrelationships/family/{family}         | GET    | Family relationship details                                    |

  Subjects & Classes API

  | Endpoint                                                     | Method | Returns
                              |
  |--------------------------------------------------------------|--------|--------------------------------------------------------------
  ----------------------------|
  | /api/subjects/get_by_grade/{grade}                           | GET    | Subjects for specific grade (name, short code, category)
                              |
  | /api/subjects/get_by_grades/{gradeString}                    | GET    | Subjects for multiple grades
                              |
  | /api/classes/pupilteachers/{pupil}                           | GET    | Teachers and classes for pupil (class details, subject, staff
   info, teaching assistants) |
  | /api/classes/bygradeperiodsubject/{grade}/{period}/{subject} | GET    | Classes matching grade, period, and subject
                              |
  | /api/registrations/grade/{grade}                             | GET    | Class registrations for specific grade
                              |

  Assessments & Reporting API

  | Endpoint                                      | Method | Returns
       |
  |-----------------------------------------------|--------|-----------------------------------------------------------------------------
  -----|
  | /api/assessment/recentresults/{pupil}         | GET    | Recent assessment results (description, date, total, weighting, result,
  subject) |
  | /api/questions/questionbreakdown/{assessment} | GET    | Question statistics (question number, marks, average score, pass rate)
       |
  | /api/reporting/pupilreportingperiods/{pupil}  | GET    | Available reporting periods for pupil (dates, aggregates, document info)
       |
  | /api/reporting/periods/{year}                 | GET    | All reporting periods for specific year
       |
  | /api/reporting/results/{period}               | GET    | Reporting results for all pupils in period
       |
  | /api/reporting/subjectmarksbypupil/{pupil}    | GET    | Subject marks across all periods (teacher, result, class)
       |
  | /api/reporting/markbook/{period}/{pupil}      | GET    | Detailed markbook/assessment data (categories, assessments, results,
  comments)   |
  | /api/reporting/report/{period}/{pupil}        | GET    | Pupil report document (binary PDF)
       |
  | /api/reporting/previousreports/{pupil}        | GET    | List of previous reports
       |

  Medical Module

  | Endpoint                     | Method | Returns                                                               |
  |------------------------------|--------|-----------------------------------------------------------------------|
  | /api/medical/offsport/{date} | GET    | Array of pupil IDs who cannot participate in sports on specified date |

  Leaves Module

  | Endpoint                         | Method | Returns                                        |
  |----------------------------------|--------|------------------------------------------------|
  | /api/leaves/approved/{from}/{to} | GET    | Approved leave requests (pupil, dates, reason) |

  Absentees Module

  | Endpoint                                         | Method | Returns
    |
  |--------------------------------------------------|--------|--------------------------------------------------------------------------
  --|
  | /api/absentees/daysabsentforpupil/{pupil}/{year} | GET    | Days absent for pupil (dates, reasons, notes)
    |
  | /api/absentees/summarycount/{from}/{to}          | GET    | Absentee counts for all pupils in date range
    |
  | /api/absentees/list/{from}/{to}                  | GET    | Detailed absentee list (pupil, date, reason, notes)
    |
  | /api/absenteekiosk/register/{pupil}              | POST   | Registration status (Present/Late/Not registered) with color-coded
  message |

  Applications Module

  | Endpoint                                | Method | Returns                                                  |
  |-----------------------------------------|--------|----------------------------------------------------------|
  | /api/applications/verifyid/{idNumber}   | GET    | ID validation status (valid, exists, pupil_id if exists) |
  | /api/applications/apply                 | POST   | New application and pupil IDs                            |
  | /api/applications/applicationformfields | GET    | Application form field definitions                       |

  Records and Points Module

  | Endpoint                                               | Method | Returns
          |
  |--------------------------------------------------------|--------|--------------------------------------------------------------------
  --------|
  | /api/recordsandpoints/recentpupilrecords/{pupil}       | GET    | Recent achievements/disciplinary records (date, type, description,
  points) |
  | /api/recordsandpoints/pupilrecords/{pupil}/{from}/{to} | GET    | All records for pupil in date range (with staff name)
          |

  Psychometric Module

  | Endpoint                                                   | Method | Returns
       |
  |------------------------------------------------------------|--------|----------------------------------------------------------------
  -----|
  | /api/psychometric/assessmentsbycategory/{pupil}/{category} | GET    | Psychometric assessments by category (assessment name, date,
  score) |

  Messaging Logs Module

  | Endpoint                                | Method | Returns                                                      |
  |-----------------------------------------|--------|--------------------------------------------------------------|
  | /api/messaginglogs/messages/{from}/{to} | GET    | Messaging logs (subject, date, type, recipient count)        |
  | /api/messaginglogs/message/{message}    | GET    | Specific message details (subject, body, recipients, status) |
  | /api/messaginglogs/messagebyid/{id}     | GET    | Message by unique identifier                                 |

  Family Login Privileges Module

  | Endpoint                             | Method | Returns                                                              |
  |--------------------------------------|--------|----------------------------------------------------------------------|
  | /api/familylogin/privileges/{family} | GET    | Family login privileges (marks, reports, absentee, financial access) |

  DevMan Export Module

  | Endpoint                     | Method | Returns                                               |
  |------------------------------|--------|-------------------------------------------------------|
  | /api/xdevman/alumni          | GET    | Alumni data (pupil info, admin number, year left)     |
  | /api/xdevman/leavers         | GET    | Recent leavers data                                   |
  | /api/xdevman/currentpupils   | GET    | Current pupils data (pupil info, admin number, grade) |
  | /api/xdevman/alumnus/{pupil} | GET    | Single alumnus data                                   |

  Staff API

  | Endpoint                         | Method | Returns                       |
  |----------------------------------|--------|-------------------------------|
  | /api/staff/image/{staff}/{width} | GET    | Staff photo (binary JPEG/PNG) |

  Admissions API

  | Endpoint                     | Method | Returns                                                  |
  |------------------------------|--------|----------------------------------------------------------|
  | /api/registration/statuslist | GET    | Registration status definitions (id, description, stage) |
  | /api/registration/statuses   | GET    | All pupil registration statuses (pupil, status, date)    |
  | /api/registration/status     | POST   | Status update confirmation                               |

  System Utilities APIs

  | Endpoint                                          | Method | Returns                                                              |
  |---------------------------------------------------|--------|----------------------------------------------------------------------|
  | /api/cron/cronlog/{limit}                         | GET    | Cron job execution logs (job name, execution time, status, duration) |
  | /api/changelog/undo/{change}                      | POST   | Undo confirmation                                                    |
  | /api/migration/version                            | GET    | Migration/export version information                                 |
  | /api/migration/tablelist                          | GET    | Database tables available for migration                              |
  | /api/migration/tablerows/{table}                  | GET    | Row count for migration table                                        |
  | /api/migration/tabledata/{table}/{offset}/{limit} | GET    | Table data for migration/export                                      |
  | /api/migration/docrepfile/{document}              | GET    | Document repository file (binary)                                    |
  | /api/tablefields/fields/{table}/{action}          | GET    | Table field definitions (type, required, editable, max_length)       |
  | /api/formfields/fields/{form}                     | GET    | Form field definitions (id, name, type, label, required)             |
  | /api/export/families                              | GET    | Family data for integrations (family info, children)                 |

  Total: 70+ endpoints across 17 categories

  Key Notes:
  - All endpoints use path parameters (e.g., /api/pupils/pupil/123), NOT query parameters
  - Most require Bearer token authentication
  - Dates use YYYY-MM-DD format
  - Binary responses (images, PDFs) return raw data without JSON wrapping
  - All JSON responses follow format: {"data": {}, "message": "", "response": {"code": 200, "error": ""}}