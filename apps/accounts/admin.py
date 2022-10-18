from django.contrib import admin

from .forms import AccountAdminForm, ActivityAdminForm, GroupAdminForm, RequestAdminForm
from .models import Account, Activity, Group, Request


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'username',
        'date_joined',
        'role',
        'is_active',
        'deleted',
    )
    list_display_links = ('uuid', )
    form = AccountAdminForm
    actions = (
        'enable',
        'disable',
        'restore',
        'logical_erase'
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name'
    )

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

    enable.description = 'Enable User(s)'
    disable.description = 'Disable User(s)'
    logical_erase.description = 'Delete User(s)'
    restore.description = 'Restore User(s)'


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'ext_id',
        'name',
        'group',
        'start_date',
        'status'
    )
    list_filter = (
        'status',
        'group'
    )
    search_fields = (
        'name',
        # 'group'
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'name',
        'description',
        'email',
        'is_active'
    )
    list_display_links = ('uuid', )
    form = GroupAdminForm

    search_fields = (
        'uuid',
        'name',
        'description',
        'email',
    )


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = (
        'uuid',
        'title',
        'description',
        'group_id',
        'date_start',
        'date_end',
        'category',
        'status'
    )
    list_display_links = ('uuid', )
    form = RequestAdminForm
    search_fields = (
        'uuid',
        'title',
        'description',
        'category',
    )
