from django.contrib import admin

from .models import Record, Zone
from apps.accounts.models import Account
from apps.utils.choices import PROMOTER, SUPERVISOR


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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["promoter"].queryset = Account.objects.filter(role=PROMOTER)
        form.base_fields["supervisor"].queryset = Account.objects.filter(
            role=SUPERVISOR
        )
        return form


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("pk", "name")
    list_display_links = ("name",)
    search_fields = ("name",)
