# 🔄 ADOSX Reconciliation Dashboard

A full-stack **data reconciliation dashboard** built for the ADOSX Engineering Full-Stack Engineer take-home assignment.

The application imports records from two independent systems, handles dirty and inconsistent CSV data, reconciles records within their organization boundary, and displays the disagreements through a React dashboard.

The implementation focuses on correctness, dirty-data handling, tenant-safe matching, testable comparison logic, and a clear working feature rather than unnecessary visual complexity.

---

# 🚀 What I Built

## 📥 CSV Data Import

The application imports three CSV files:

* `system_a.csv`
* `system_b.csv`
* `locations.csv`

The importer:

* Imports all source rows into the database
* Preserves dirty and blank values
* Normalizes inconsistent System B record references
* Handles comma-formatted numeric values
* Preserves the original source row using `raw_data`
* Stores the original CSV row number
* Preserves duplicate System B entries
* Does not silently drop invalid rows

### Imported Data

The supplied dataset contains:

| Data | Count |
|---|---:|
| Organizations | 2 |
| Locations | 5 |
| System A records | 120 |
| System B entries | 121 |

---

# 🔍 Reconciliation

The application compares records from System A and System B and identifies disagreements.

## 🔗 Tenant-Safe Record Matching

System B references are normalized before matching.

Examples of supported dirty references:

* `rec1034`
* `REC - 1070`
* `1112`

Records are matched using:

```text
Organization + Normalized Record Reference

This prevents records from different organizations from being incorrectly matched.

❌ Missing in System B

Detects a System A record that has no corresponding System B entry within the same organization.

Reason:

missing_in_system_b
⚠️ Orphan System B Entry

Detects a System B entry whose organization and normalized record reference do not correspond to a System A record.

Reason:

orphan_system_b
🔁 Duplicate System B Entry

Detects when multiple System B entries refer to the same record within an organization.

Reason:

duplicate_in_system_b

Duplicate source rows are preserved instead of being deleted.

💰 Value Mismatch

The application compares:

System A → total_value
System B → value

Numeric values are parsed before comparison so that formatting differences such as commas do not create false mismatches.

Blank values are also handled safely.

Reason:

value_mismatch
📊 Reconciliation Result

For the supplied dataset, the tenant-safe comparison produces:

Disagreement Type	Count
Value mismatches	5
Missing in System B	3
Duplicate System B references	2
Orphan System B entries	2
Total disagreements	12

The additional missing/orphan result is caused by a record reference appearing under different organizations.

For example:

System A:
ORG-A + REC-1077

and:

System B:
ORG-B + REC-1077

are treated as different reconciliation records because organization is part of the matching key.

👥 Organization / Tenant Boundary

Every location belongs to exactly one organization.

The database relationship is:

Organization
     │
     └── Location
            │
            ├── System A Record
            │
            └── System B Entry

The reconciliation logic uses:

Organization + Normalized Record Reference

as the comparison boundary.

Therefore, the same record reference cannot be incorrectly matched across organizations.

Authentication was intentionally not implemented because authentication is outside the requested scope of the assignment.

🖥️ Dashboard

The React dashboard displays every disagreement in a simple table.

The table contains:

Reason
Record ID
Field
System A value
System B value
Location
Organization

The UI intentionally remains simple because the assignment prioritizes a working reconciliation feature over visual design.

🎯 Filtering

The dashboard allows disagreements to be filtered by reason.

Available filters:

All
Value mismatch
Missing in System B
Duplicate in System B
Orphan System B

The backend also supports filtering through the API.

Example:

/api/disagreements/?reason=value_mismatch
↕️ Sorting

The dashboard supports sorting disagreements by value.

Ascending:

/api/disagreements/?sort=value

Descending:

/api/disagreements/?sort=-value
🔌 API

The backend provides a REST API for the reconciliation results.

Get all disagreements
GET /api/disagreements/
Filter by reason
GET /api/disagreements/?reason=value_mismatch
GET /api/disagreements/?reason=missing_in_system_b
GET /api/disagreements/?reason=duplicate_in_system_b
GET /api/disagreements/?reason=orphan_system_b
Sort by value
GET /api/disagreements/?sort=value
GET /api/disagreements/?sort=-value
🧪 Testing

Tests focus on the reconciliation logic where disagreements are decided.

The current test suite contains:

12 tests
12 passed

Tests cover:

Missing System B records
Orphan System B entries
Duplicate System B entries
Value mismatches
Matching records
Dirty record references
Comma-formatted numeric values
Blank values
API response
API filtering
Empty filter results
Cross-tenant record isolation

Run the tests:

cd backend
python manage.py test reconciliation

Expected:

Ran 12 tests

OK
🛠️ Tech Stack
Layer	Technology
Backend	Django
API	Django REST Framework
Frontend	React
Build Tool	Vite
Database	SQLite
Language	Python
Styling	CSS
Testing	Django Test Framework
Version Control	Git
Repository	GitHub
📁 Project Structure
adosx-reconciliation/
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   └── reconciliation/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── comparison.py
│       ├── serializers.py
│       ├── urls.py
│       ├── views.py
│       ├── tests.py
│       ├── migrations/
│       │
│       └── management/
│           ├── __init__.py
│           └── commands/
│               ├── __init__.py
│               └── import_csv.py
│
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── App.css
│       └── api.js
│
├── data/
│   ├── system_a.csv
│   ├── system_b.csv
│   └── locations.csv
│
├── README.md
├── DECISIONS.md
└── .gitignore
⚙️ How to Run
🔹 1. Clone the Repository
git clone <YOUR_PRIVATE_REPOSITORY_URL>

cd adosx-reconciliation
🐍 Backend
🔹 2. Create Virtual Environment
cd backend

python -m venv venv
Windows
.\venv\Scripts\Activate.ps1
🔹 3. Install Dependencies
pip install -r requirements.txt
🔹 4. Create Database
python manage.py migrate
🔹 5. Import CSV Data
python manage.py import_csv

This imports:

../data/locations.csv
../data/system_a.csv
../data/system_b.csv
🔹 6. Run Tests
python manage.py test reconciliation

Expected:

Ran 12 tests

OK
🔹 7. Start Django
python manage.py runserver

Backend:

http://127.0.0.1:8000/
⚛️ Frontend

Open a new terminal.

🔹 1. Navigate to Frontend
cd frontend
🔹 2. Install Dependencies
npm install
🔹 3. Start React
npm run dev

Frontend:

http://localhost:5173/
📱 Application Flow
Import locations and organization mappings
Import System A records
Import System B entries
Normalize System B record references
Match records within the organization boundary
Detect missing records
Detect orphan entries
Detect duplicate entries
Compare values
Return disagreements through the API
Display disagreements in the React dashboard
Filter by reason
Sort by value
🤖 How I Worked With the Agent

I used limited AI assistance during the assignment as a development aid.

I used the agent mainly for:

Understanding Django and React implementation details
Reviewing implementation approaches
Debugging development errors
Identifying edge cases
Improving test coverage
Reviewing parts of the documentation

I did not treat AI-generated code as automatically correct. I ran the application, inspected the supplied dataset, compared the reconciliation results, and ran the automated tests before accepting changes.

The most important example was the tenant-boundary issue described below.

❌ What I Deliberately Did Not Build

The assignment explicitly excludes several areas from evaluation, so I intentionally kept them out of scope.

I did not build:

Authentication
Login functionality
Role-based authorization
Production deployment
Advanced performance optimization
Server-side pagination
Background job processing
Real-time updates
Complex UI design

The goal was to deliver a small, complete, and well-tested reconciliation feature rather than a larger partially implemented system.

🚧 Challenges Faced

The main challenges were:

Handling dirty System B record references
Preserving malformed or blank source values
Handling duplicate System B entries
Parsing differently formatted numeric values
Handling records that do not exist in the other system
Enforcing organization boundaries during reconciliation
Separating comparison logic from API logic

The cross-organization REC-1077 case was particularly important because it showed that matching globally by record reference could produce an incorrect tenant match.

📌 Design Decisions

The main architectural decisions are documented in:

DECISIONS.md

The file contains 10 short decisions covering:

Technology selection
Database choice
Source table design
Dirty-data handling
Reference normalization
Duplicate handling
Value comparison
Organization boundaries
Comparison logic separation
Scope management

Each entry contains the decision, the alternative that was rejected, and the reasoning that separated the two approaches.

🤖 How I Verified the Agent's Work

The AI-generated suggestions were verified by:

Running the Django test suite
Inspecting imported row counts
Inspecting the actual CSV data
Checking dirty reference cases
Checking duplicate cases
Checking value mismatches
Checking cross-organization records
Testing the API filters
Testing the frontend against the backend API

The final implementation was not accepted based solely on AI output.

👩‍💻 Author

Rachana Hegde

B.Tech Graduate | Full-Stack / Backend / Data & AI Enthusiast

GitHub:

https://github.com/Rachana-Hegde
📝 Required Assignment Questions
a. Name one thing the AI agent got wrong. How did you notice?

The initial comparison logic matched records using only the normalized record reference. This did not properly enforce the organization boundary.

I noticed this while inspecting the location-to-organization mapping. REC-1077 existed in System A under ORG-A, while System B contained the same reference under ORG-B. I changed the matching key to organization plus normalized record reference and added a test to prevent cross-tenant matching.

b. Which part of your submission are you least confident about, and why?

I am least confident about production-level tenant isolation because authentication and user context were explicitly outside the scope of this assignment.

The current implementation enforces the organization boundary during reconciliation using the organization associated with each location. In a production system, I would additionally enforce organization-level filtering at the API/query layer using the authenticated tenant.

c. If you had a second day, what would you fix first?

I would first strengthen the tenant boundary at the API layer by introducing an explicit tenant context and organization-level query filtering.

I would also add more edge-case tests for malformed references, missing locations, invalid numeric values, and additional cross-organization scenarios.
