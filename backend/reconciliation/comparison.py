from decimal import Decimal, InvalidOperation
import re


def normalize_record_reference(value):
    if value is None:
        return ""

    value = str(value).strip().upper()

    if not value:
        return ""

    match = re.search(r"(\d+)$", value)

    if match:
        return f"REC-{match.group(1)}"

    return value


def parse_decimal(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace(",", "")

    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def values_equal(a_value, b_value):
    a_number = parse_decimal(a_value)
    b_number = parse_decimal(b_value)

    if a_number is not None and b_number is not None:
        return a_number == b_number

    return (
        str(a_value or "").strip().lower()
        == str(b_value or "").strip().lower()
    )


def location_name(record):
    if record.location:
        return record.location.location_name
    return None


def organization_id(record):
    if record.location and record.location.organization:
        return record.location.organization.org_id
    return None


def record_key(record):
    """
    Creates a tenant-safe comparison key using the organization
    and normalized record reference.
    """
    return (
        organization_id(record),
        normalize_record_reference(record.record_id),
    )


def b_entry_key(entry):
    """
    Creates the same tenant-safe key for a System B entry.
    """
    organization = None

    if entry.location and entry.location.organization:
        organization = entry.location.organization.org_id

    return (
        organization,
        normalize_record_reference(entry.record_ref),
    )


def compare_record(a_record, b_entries):
    disagreements = []

    location = location_name(a_record)
    organization = organization_id(a_record)

    if not b_entries:
        disagreements.append(
            {
                "reason": "missing_in_system_b",
                "record_id": a_record.record_id,
                "field": "record",
                "system_a_value": a_record.record_id,
                "system_b_value": None,
                "system_a": a_record.raw_data,
                "system_b": None,
                "location": location,
                "organization": organization,
            }
        )
        return disagreements

    if len(b_entries) > 1:
        disagreements.append(
            {
                "reason": "duplicate_in_system_b",
                "record_id": a_record.record_id,
                "field": "record",
                "system_a_value": a_record.record_id,
                "system_b_value": [
                    entry.record_ref
                    for entry in b_entries
                ],
                "system_a": a_record.raw_data,
                "system_b": [
                    entry.raw_data
                    for entry in b_entries
                ],
                "location": location,
                "organization": organization,
            }
        )
        return disagreements

    b_entry = b_entries[0]

    if not values_equal(
        a_record.total_value,
        b_entry.value,
    ):
        disagreements.append(
            {
                "reason": "value_mismatch",
                "record_id": a_record.record_id,
                "field": "total_value",
                "system_a_value": a_record.total_value,
                "system_b_value": b_entry.value,
                "system_a": a_record.raw_data,
                "system_b": b_entry.raw_data,
                "location": location,
                "organization": organization,
            }
        )

    return disagreements


def find_orphan_entries(a_records, b_entries):
    """
    An entry is an orphan when its organization + normalized
    record reference does not exist in System A.
    """
    a_keys = {
        record_key(record)
        for record in a_records
    }

    disagreements = []

    for entry in b_entries:
        key = b_entry_key(entry)

        if key not in a_keys:
            location = (
                entry.location.location_name
                if entry.location
                else None
            )

            organization = (
                entry.location.organization.org_id
                if entry.location
                and entry.location.organization
                else None
            )

            disagreements.append(
                {
                    "reason": "orphan_system_b",
                    "record_id": entry.record_ref,
                    "field": "record",
                    "system_a_value": None,
                    "system_b_value": entry.record_ref,
                    "system_a": None,
                    "system_b": entry.raw_data,
                    "location": location,
                    "organization": organization,
                }
            )

    return disagreements


def build_disagreements(a_records, b_entries):
    """
    Build disagreements while keeping records inside their
    organization/tenant boundary.

    Matching key:
        (organization_id, normalized_record_reference)
    """

    b_by_key = {}

    for entry in b_entries:
        key = b_entry_key(entry)

        if key[1]:
            b_by_key.setdefault(key, []).append(entry)

    disagreements = []

    for a_record in a_records:
        key = record_key(a_record)

        matching_entries = b_by_key.get(
            key,
            [],
        )

        disagreements.extend(
            compare_record(
                a_record,
                matching_entries,
            )
        )

    disagreements.extend(
        find_orphan_entries(
            a_records,
            b_entries,
        )
    )

    return disagreements