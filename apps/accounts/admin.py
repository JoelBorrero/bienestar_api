from django.contrib import admin

from .forms import AccountAdminForm, GroupAdminForm
from .models import Account, Activity, Group


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "date_joined",
        "role",
        "is_active",
        "deleted",
    )
    list_filter = ("role",)
    form = AccountAdminForm
    actions = ("enable", "disable", "restore", "logical_erase")
    search_fields = ("username", "first_name", "last_name")

    def enable(self, request, queryset):
        for ad in queryset:
            ad.enable()

    def disable(self, request, queryset):
        for ad in queryset:
            ad.disable()

    def logical_erase(self, request, queryset):
        for ad in queryset:
            ad.logical_erase()

    def restore(self, request, queryset):
        for ad in queryset:
            ad.restore()

    enable.description = "Enable User(s)"
    disable.description = "Disable User(s)"
    logical_erase.description = "Delete User(s)"
    restore.description = "Restore User(s)"


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("ext_id", "name", "group", "start_date", "status")
    list_filter = ("status", "group")
    search_fields = ("name",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "username", "description", "is_active")
    list_display_links = ("name",)
    form = GroupAdminForm
    search_fields = (
        "pk",
        "name",
        "description",
        "username",
    )
