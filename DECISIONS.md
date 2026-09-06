# Design Decisions

## 1. Django + React

**Decision:** Use Django REST Framework for the backend and React for the frontend.

**Rejected alternative:** Use a single Django-rendered frontend.

**Reason:** Django + React matches the preferred stack and gives a clear separation between the API and UI.

---

## 2. SQLite

**Decision:** Use SQLite for the assignment database.

**Rejected alternative:** Use PostgreSQL.

**Reason:** The dataset is small and SQLite keeps local setup simple while still demonstrating proper relational table design.

---

## 3. Separate Source Tables

**Decision:** Store System A and System B in separate database tables.

**Rejected alternative:** Merge both sources into one normalized event table.

**Reason:** Keeping the sources separate preserves their original versions and makes reconciliation explicit.

---

## 4. Preserve Dirty Data

**Decision:** Preserve dirty values and the original CSV row data instead of dropping invalid rows.

**Rejected alternative:** Reject malformed rows during import.

**Reason:** The assignment explicitly requires the importer to survive dirty exports without silently dropping data.

---

## 5. Normalize Record References

**Decision:** Normalize System B record references before matching.

**Rejected alternative:** Require System B references to exactly match System A identifiers.

**Reason:** Real exports may contain variations such as `rec1034`, `REC - 1070`, and `1112`.

---

## 6. Do Not Deduplicate System B

**Decision:** Preserve multiple System B entries for the same record.

**Rejected alternative:** Keep only the first or last duplicate.

**Reason:** A duplicate is itself a disagreement that must be visible to the user.

---

## 7. Compare Total Value

**Decision:** Compare System A `total_value` with System B `value`.

**Rejected alternative:** Compare the raw strings directly.

**Reason:** Numeric formatting differences such as commas should not create false disagreements.

---

## 8. Organization Boundary

**Decision:** Associate every location with an organization and perform reconciliation within that organization boundary.

**Rejected alternative:** Match records globally using only the record reference.

**Reason:** The assignment requires tenant data to remain isolated and never leak across organizations.

---

## 9. Separate Comparison Logic

**Decision:** Keep reconciliation rules in `comparison.py`.

**Rejected alternative:** Put comparison logic directly inside the API view.

**Reason:** Separating the decision logic makes it easier to test and reason about independently from the HTTP layer.

---

## 10. Focus on Required Scope

**Decision:** Implement importing, reconciliation, filtering, sorting, and tests without adding authentication or unnecessary production infrastructure.

**Rejected alternative:** Spend the assignment time on authentication, deployment, or extensive UI features.

**Reason:** The brief explicitly says those areas are not being tested and prioritizes a small, complete, well-reasoned solution.