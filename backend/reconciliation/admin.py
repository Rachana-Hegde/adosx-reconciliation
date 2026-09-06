from django.contrib import admin

from reconciliation.models import (
    Organization,
    Location,
    SystemARecord,
    SystemBEntry,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = (
        "org_id",
    )
    search_fields = (
        "org_id",
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "location_id",
        "location_name",
        "organization",
    )
    search_fields = (
        "location_id",
        "location_name",
        "organization__org_id",
    )
    list_filter = (
        "organization",
    )


@admin.register(SystemARecord)
class SystemARecordAdmin(admin.ModelAdmin):
    list_display = (
        "record_id",
        "location",
        "total_value",
        "state",
    )
    search_fields = (
        "record_id",
        "location__location_id",
    )
    list_filter = (
        "state",
    )


@admin.register(SystemBEntry)
class SystemBEntryAdmin(admin.ModelAdmin):
    list_display = (
        "entry_id",
        "record_ref",
        "normalized_record_ref",
        "location",
        "value",
    )
    search_fields = (
        "entry_id",
        "record_ref",
        "normalized_record_ref",
    )
    list_filter = (
        "location",
    )