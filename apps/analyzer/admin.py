from django.contrib import admin

from .models import UploadedReport

@admin.register(UploadedReport)
class UploadedReportAdmin(admin.ModelAdmin):
    list_display = [
        'uuid',
        'result',
        'created_at'
    ]
    list_display_links = [
        'uuid'
    ]
