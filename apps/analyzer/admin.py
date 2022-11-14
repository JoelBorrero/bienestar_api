from django.contrib import admin

from .models import UploadedReport


@admin.register(UploadedReport)
class UploadedReportAdmin(admin.ModelAdmin):
    list_display = ("pk", "result", "created_at")
