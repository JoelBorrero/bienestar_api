from django.contrib import admin

from .models import Record, UploadedReport, Zone


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "supervisor",
        "promoter",
        "zone",
        "start_date",
        "wake_up_calls",
        "supervisor_wake_up_calls",
        "is_signed",
    )
    list_filter = ("is_signed", "zone", "supervisor", "promoter")


@admin.register(UploadedReport)
class UploadedReportAdmin(admin.ModelAdmin):
    list_display = ("pk", "result", "created_at")


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("pk", "name")
    list_display_links = ("name",)
    search_fields = ("name",)
