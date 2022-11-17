from rest_framework.permissions import BasePermission

from .choices import PROMOTER, SUPERVISOR
from apps.utils.exceptions import RegisterDisabledValidationError
from apps.utils.redis import client as redis


class IsAccount(BasePermission):
    """
    Allows access only to account users.
    """

    def has_permission(self, request, view):
        return hasattr(request.user, "account")


class IsPromoter(BasePermission):
    """
    Allows access only to promoters.
    """

    def has_permission(self, request, view):
        if hasattr(request.user, "account"):
            return bool(request.user.account.role == PROMOTER)
        return False


class IsRegisterEnabled(BasePermission):
    """
    Allows access when register allow_register=True
    """

    def has_permission(self, request, view):
        if not redis.get_json("setup").get("allow_register"):
            raise RegisterDisabledValidationError()
        return True


class IsSupervisor(BasePermission):
    """
    Allows access only to supervisors.
    """

    def has_permission(self, request, view):
        if hasattr(request.user, "account"):
            return bool(request.user.account.role == SUPERVISOR)
        return False
