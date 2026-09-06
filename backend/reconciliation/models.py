from django.db import models


class Organization(models.Model):
    org_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.org_id


class Location(models.Model):
    location_id = models.CharField(max_length=50, unique=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="locations",
    )
    location_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.location_id} - {self.location_name}"


class SystemARecord(models.Model):
    record_id = models.CharField(max_length=100, unique=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="system_a_records",
        null=True,
        blank=True,
    )

    event_date = models.CharField(max_length=100, blank=True)
    category_code = models.CharField(max_length=100, blank=True)
    actor_id = models.CharField(max_length=100, blank=True)

    # Keep source values as text so dirty CSV data is never silently lost.
    base_value = models.CharField(max_length=100, blank=True)
    adjustment = models.CharField(max_length=100, blank=True)
    total_value = models.CharField(max_length=100, blank=True)

    state = models.CharField(max_length=100, blank=True)

    # Complete original CSV row.
    raw_data = models.JSONField(default=dict)

    # Original CSV row number for traceability.
    row_number = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.record_id


class SystemBEntry(models.Model):
    entry_id = models.CharField(max_length=100, unique=True)

    # Do NOT make this unique.
    # The assignment deliberately contains duplicate references.
    record_ref = models.CharField(max_length=100, blank=True)

    # Normalized version used by the comparison engine.
    normalized_record_ref = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="system_b_entries",
        null=True,
        blank=True,
    )

    recorded_on = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=255, blank=True)

    # Complete original CSV row.
    raw_data = models.JSONField(default=dict)

    # Original CSV row number for traceability.
    row_number = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.entry_id