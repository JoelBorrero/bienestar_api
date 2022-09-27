from django import forms

from .models import Account, Activity, Group, Request


class AccountAdminForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'validate_code',
            'role',
            'deleted',
            'reset_password_code',
            'raw_password'
        )
class ActivityAdminForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = (
            'name',
            'description',
            'group',
            'date',
            'location_name'
        )
class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = (
            'name',
            'description',
            'email',
            'is_active'
        )
class RequestAdminForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = (
            'title',
            'description',
            'group_id',
            'date_start',
            'date_end',
            'category',
            'status'
        )
