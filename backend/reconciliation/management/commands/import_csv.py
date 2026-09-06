import csv
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from reconciliation.models import (
    Organization,
    Location,
    SystemARecord,
    SystemBEntry,
)


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


def normalize_record_reference(value):
    """
    Convert dirty System B references into a common format.

    Examples:
        rec1034   -> REC-1034
        REC - 1070 -> REC-1070
        1112      -> REC-1112
        REC-1003  -> REC-1003
    """
    value = clean(value).upper()

    if not value:
        return ""

    match = re.search(r"(\d+)$", value)

    if match:
        return f"REC-{match.group(1)}"

    return value


class Command(BaseCommand):
    help = "Import locations.csv, system_a.csv and system_b.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--data-dir",
            default=None,
            help="Path to the folder containing the CSV files.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        project_root = Path(__file__).resolve().parents[4]

        if options["data_dir"]:
            data_dir = Path(options["data_dir"]).resolve()
        else:
            data_dir = project_root / "data"

        locations_file = data_dir / "locations.csv"
        system_a_file = data_dir / "system_a.csv"
        system_b_file = data_dir / "system_b.csv"

        files = [
            locations_file,
            system_a_file,
            system_b_file,
        ]

        for file_path in files:
            if not file_path.exists():
                raise CommandError(
                    f"CSV file not found: {file_path}"
                )

        self.stdout.write(
            self.style.WARNING(
                f"Importing CSV files from: {data_dir}"
            )
        )

        # ---------------------------------------------------------
        # Clear previous imported data.
        # This keeps development imports repeatable.
        # ---------------------------------------------------------

        SystemBEntry.objects.all().delete()
        SystemARecord.objects.all().delete()
        Location.objects.all().delete()
        Organization.objects.all().delete()

        # ---------------------------------------------------------
        # Import locations.csv
        # ---------------------------------------------------------

        location_count = 0

        with locations_file.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            required_columns = {
                "location_id",
                "org_id",
                "location_name",
            }

            self.validate_columns(
                reader.fieldnames,
                required_columns,
                locations_file,
            )

            for row_number, row in enumerate(reader, start=2):
                location_id = clean(row.get("location_id"))
                org_id = clean(row.get("org_id"))
                location_name = clean(row.get("location_name"))

                organization, _ = Organization.objects.get_or_create(
                    org_id=org_id
                )

                Location.objects.create(
                    location_id=location_id,
                    organization=organization,
                    location_name=location_name,
                )

                location_count += 1

        # ---------------------------------------------------------
        # Build location lookup
        # ---------------------------------------------------------

        locations = {
            location.location_id: location
            for location in Location.objects.select_related(
                "organization"
            )
        }

        # ---------------------------------------------------------
        # Import system_a.csv
        # ---------------------------------------------------------

        system_a_count = 0

        with system_a_file.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            required_columns = {
                "record_id",
                "location_id",
                "event_date",
                "category_code",
                "actor_id",
                "base_value",
                "adjustment",
                "total_value",
                "state",
            }

            self.validate_columns(
                reader.fieldnames,
                required_columns,
                system_a_file,
            )

            for row_number, row in enumerate(reader, start=2):
                location_id = clean(row.get("location_id"))

                location = locations.get(location_id)

                SystemARecord.objects.create(
                    record_id=clean(row.get("record_id")),
                    location=location,
                    event_date=clean(row.get("event_date")),
                    category_code=clean(row.get("category_code")),
                    actor_id=clean(row.get("actor_id")),
                    base_value=clean(row.get("base_value")),
                    adjustment=clean(row.get("adjustment")),
                    total_value=clean(row.get("total_value")),
                    state=clean(row.get("state")),
                    raw_data={
                        key: clean(value)
                        for key, value in row.items()
                    },
                    row_number=row_number,
                )

                system_a_count += 1

        # ---------------------------------------------------------
        # Import system_b.csv
        # ---------------------------------------------------------

        system_b_count = 0

        with system_b_file.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            required_columns = {
                "entry_id",
                "record_ref",
                "location_id",
                "recorded_on",
                "value",
                "label",
            }

            self.validate_columns(
                reader.fieldnames,
                required_columns,
                system_b_file,
            )

            for row_number, row in enumerate(reader, start=2):
                location_id = clean(row.get("location_id"))

                location = locations.get(location_id)

                record_ref = clean(row.get("record_ref"))

                SystemBEntry.objects.create(
                    entry_id=clean(row.get("entry_id")),
                    record_ref=record_ref,
                    normalized_record_ref=normalize_record_reference(
                        record_ref
                    ),
                    location=location,
                    recorded_on=clean(row.get("recorded_on")),
                    value=clean(row.get("value")),
                    label=clean(row.get("label")),
                    raw_data={
                        key: clean(value)
                        for key, value in row.items()
                    },
                    row_number=row_number,
                )

                system_b_count += 1

        # ---------------------------------------------------------
        # Final summary
        # ---------------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS("CSV import completed successfully!")
        )

        self.stdout.write(
            f"Locations imported : {location_count}"
        )

        self.stdout.write(
            f"System A imported  : {system_a_count}"
        )

        self.stdout.write(
            f"System B imported  : {system_b_count}"
        )

        self.stdout.write(
            f"Total source rows  : "
            f"{location_count + system_a_count + system_b_count}"
        )

    @staticmethod
    def validate_columns(
        actual_columns,
        required_columns,
        file_path,
    ):
        actual = set(actual_columns or [])

        missing = required_columns - actual

        if missing:
            raise CommandError(
                f"{file_path.name} is missing columns: "
                f"{', '.join(sorted(missing))}"
            )