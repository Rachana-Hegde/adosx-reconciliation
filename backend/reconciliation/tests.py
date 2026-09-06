from decimal import Decimal

from django.test import TestCase

from reconciliation.comparison import (
    build_disagreements,
    normalize_record_reference,
    parse_decimal,
    values_equal,
)
from reconciliation.models import (
    Organization,
    Location,
    SystemARecord,
    SystemBEntry,
)


class ComparisonLogicTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            org_id="ORG-TEST"
        )

        self.location = Location.objects.create(
            location_id="LOC-TEST",
            organization=self.organization,
            location_name="Test Location",
        )

    def create_a_record(
        self,
        record_id="REC-1001",
        total_value="1000.00",
    ):
        return SystemARecord.objects.create(
            record_id=record_id,
            location=self.location,
            event_date="2026-01-01",
            category_code="CAT-01",
            actor_id="ACT-01",
            base_value="900.00",
            adjustment="100.00",
            total_value=total_value,
            state="COMPLETED",
            raw_data={
                "record_id": record_id,
                "total_value": total_value,
            },
            row_number=2,
        )

    def create_b_entry(
        self,
        entry_id="ENT-1001",
        record_ref="REC-1001",
        value="1000.00",
    ):
        return SystemBEntry.objects.create(
            entry_id=entry_id,
            record_ref=record_ref,
            normalized_record_ref=normalize_record_reference(
                record_ref
            ),
            location=self.location,
            recorded_on="2026-01-01",
            value=value,
            label="Test",
            raw_data={
                "entry_id": entry_id,
                "record_ref": record_ref,
                "value": value,
            },
            row_number=2,
        )

    # ---------------------------------------------------------
    # 1. Missing in System B
    # ---------------------------------------------------------

    def test_missing_in_system_b(self):
        a_record = self.create_a_record()

        results = build_disagreements(
            [a_record],
            [],
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["reason"],
            "missing_in_system_b",
        )
        self.assertEqual(
            results[0]["record_id"],
            "REC-1001",
        )

    # ---------------------------------------------------------
    # 2. Orphan System B entry
    # ---------------------------------------------------------

    def test_orphan_system_b(self):
        b_entry = self.create_b_entry(
            record_ref="REC-9999"
        )

        results = build_disagreements(
            [],
            [b_entry],
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["reason"],
            "orphan_system_b",
        )
        self.assertEqual(
            results[0]["record_id"],
            "REC-9999",
        )

    # ---------------------------------------------------------
    # 3. Duplicate System B entries
    # ---------------------------------------------------------

    def test_duplicate_in_system_b(self):
        a_record = self.create_a_record()

        b_entry_1 = self.create_b_entry(
            entry_id="ENT-1001",
            record_ref="REC-1001",
            value="1000.00",
        )

        b_entry_2 = self.create_b_entry(
            entry_id="ENT-1002",
            record_ref="REC-1001",
            value="1000.00",
        )

        results = build_disagreements(
            [a_record],
            [b_entry_1, b_entry_2],
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["reason"],
            "duplicate_in_system_b",
        )

    # ---------------------------------------------------------
    # 4. Value mismatch
    # ---------------------------------------------------------

    def test_value_mismatch(self):
        a_record = self.create_a_record(
            total_value="1000.00"
        )

        b_entry = self.create_b_entry(
            value="900.00"
        )

        results = build_disagreements(
            [a_record],
            [b_entry],
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["reason"],
            "value_mismatch",
        )

        self.assertEqual(
            results[0]["system_a_value"],
            "1000.00",
        )

        self.assertEqual(
            results[0]["system_b_value"],
            "900.00",
        )

    # ---------------------------------------------------------
    # 5. Matching records produce no disagreement
    # ---------------------------------------------------------

    def test_matching_records_have_no_disagreement(self):
        a_record = self.create_a_record(
            total_value="1000.00"
        )

        b_entry = self.create_b_entry(
            value="1000.00"
        )

        results = build_disagreements(
            [a_record],
            [b_entry],
        )

        self.assertEqual(results, [])

    # ---------------------------------------------------------
    # 6. Dirty record references normalize correctly
    # ---------------------------------------------------------

    def test_dirty_record_reference_normalization(self):
        self.assertEqual(
            normalize_record_reference("rec1034"),
            "REC-1034",
        )

        self.assertEqual(
            normalize_record_reference("REC - 1070"),
            "REC-1070",
        )

        self.assertEqual(
            normalize_record_reference("1112"),
            "REC-1112",
        )

    # ---------------------------------------------------------
    # 7. Comma-formatted numeric values
    # ---------------------------------------------------------

    def test_comma_formatted_values(self):
        self.assertEqual(
            parse_decimal("1,25,400.00"),
            Decimal("125400.00"),
        )

        self.assertTrue(
            values_equal(
                "125400.00",
                "1,25,400.00",
            )
        )

    # ---------------------------------------------------------
    # 8. Blank values are handled safely
    # ---------------------------------------------------------

    def test_blank_value(self):
        self.assertIsNone(
            parse_decimal("")
        )

        self.assertIsNone(
            parse_decimal(None)
        )
        
    def test_same_record_reference_in_different_organizations_does_not_match(self):
        org_a = Organization.objects.create(org_id="TEST-ORG-A")
        org_b = Organization.objects.create(org_id="TEST-ORG-B")

        location_a = Location.objects.create(
            location_id="TEST-LOC-A",
            organization=org_a,
            location_name="Test Location A",
        )

        location_b = Location.objects.create(
            location_id="TEST-LOC-B",
            organization=org_b,
            location_name="Test Location B",
        )

        a_record = SystemARecord.objects.create(
            record_id="REC-9001",
            location=location_a,
            total_value="1000",
            raw_data={
                "record_id": "REC-9001",
                "total_value": "1000",
            },
        )

        b_entry = SystemBEntry.objects.create(
            entry_id="TEST-B-9001",
            record_ref="REC-9001",
            normalized_record_ref="REC-9001",
            location=location_b,
            value="1000",
            raw_data={
                "entry_id": "TEST-B-9001",
                "record_ref": "REC-9001",
                "value": "1000",
            },
        )

        result = build_disagreements(
            [a_record],
            [b_entry],
        )

        reasons = [
            item["reason"]
            for item in result
        ]

        self.assertIn(
            "missing_in_system_b",
            reasons,
        )

        self.assertIn(
            "orphan_system_b",
            reasons,
        )
        
from rest_framework.test import APITestCase
from rest_framework import status


class DisagreementAPITests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            org_id="ORG-API"
        )

        self.location = Location.objects.create(
            location_id="LOC-API",
            organization=self.organization,
            location_name="API Test Location",
        )

    def create_a_record(
        self,
        record_id="REC-2001",
        total_value="1000.00",
    ):
        return SystemARecord.objects.create(
            record_id=record_id,
            location=self.location,
            event_date="2026-01-01",
            category_code="CAT-01",
            actor_id="ACT-01",
            base_value="900.00",
            adjustment="100.00",
            total_value=total_value,
            state="COMPLETED",
            raw_data={
                "record_id": record_id,
                "total_value": total_value,
            },
            row_number=2,
        )

    def create_b_entry(
        self,
        entry_id="ENT-2001",
        record_ref="REC-2001",
        value="900.00",
    ):
        return SystemBEntry.objects.create(
            entry_id=entry_id,
            record_ref=record_ref,
            normalized_record_ref=normalize_record_reference(
                record_ref
            ),
            location=self.location,
            recorded_on="2026-01-01",
            value=value,
            label="API Test",
            raw_data={
                "entry_id": entry_id,
                "record_ref": record_ref,
                "value": value,
            },
            row_number=2,
        )

    def test_disagreements_endpoint_returns_results(self):
        a_record = self.create_a_record()
        b_entry = self.create_b_entry()

        response = self.client.get(
            "/api/disagreements/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["reason"],
            "value_mismatch",
        )

    def test_disagreements_endpoint_filters_by_reason(self):
        a_record = self.create_a_record()

        b_entry = self.create_b_entry()

        response = self.client.get(
            "/api/disagreements/?reason=value_mismatch"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_disagreements_endpoint_returns_empty_for_unmatched_filter(
        self,
    ):
        a_record = self.create_a_record()
        b_entry = self.create_b_entry()

        response = self.client.get(
            "/api/disagreements/?reason=orphan_system_b"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )