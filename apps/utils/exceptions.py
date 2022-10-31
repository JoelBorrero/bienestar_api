from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class DateValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Dates must be closed in 0 or 30 minutes.')
    default_code = 'date_error'


class EmailValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Email already exists.')
    default_code = 'email_exists'


class RegisterDisabledValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Register disabled.')
    default_code = 'register_disabled'


class PeopleValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('People must be different.')
    default_code = 'people_error'


class SupervisorValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Selected supervisor and was_supervised field didn't match.")
    default_code = 'supervisor_error'
