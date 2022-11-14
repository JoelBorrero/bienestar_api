from django import forms

from .models import Account, Activity, Group


class AccountAdminForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = (
            "username",
            "first_name",
            "last_name",
            "validate_code",
            "role",
            "deleted",
            "reset_password_code",
            "raw_password",
            "is_staff",
            "is_superuser",
        )


class ActivityAdminForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = (
            "name",
            "description",
            # 'group',
            "start_date",
        )


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name", "description", "is_active") + AccountAdminForm.Meta.fields
