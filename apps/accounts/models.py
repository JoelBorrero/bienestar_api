from django.contrib.gis.db import models

from django_lifecycle import AFTER_CREATE, BEFORE_UPDATE, hook

from apps.utils.constants import ACTIVITY_CATEGORIES, ACTIVITY_STATUSES, REQUEST_STATUSES
from apps.utils.models import BaseModel, BaseModelUser
from apps.utils.redis import client as redis


class Account(BaseModelUser):
    ciu = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    @hook(AFTER_CREATE)
    def on_create(self):
        if redis.get_json('setup').get('disable_user_when_register'):
            self.disable()
        self.set_raw_password()

    @hook(BEFORE_UPDATE)
    def on_update(self):
        self.set_raw_password()

class Group(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    email = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class Activity(BaseModel):
    id = models.CharField(max_length=15, unique=True)
    email = models.CharField(max_length=50)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    responsible = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    category = models.CharField(max_length=3, choices=ACTIVITY_CATEGORIES)
    is_virtual = models.BooleanField()
    institutional = models.CharField(max_length=50)
    bienestar = models.CharField(max_length=50)
    has_guests = models.BooleanField()
    guests_info = models.CharField(max_length=100)
    local_guests = models.PositiveSmallIntegerField(default=0)
    national_guests = models.PositiveSmallIntegerField(default=0)
    international_guests = models.PositiveSmallIntegerField(default=0)
    event_url = models.CharField(max_length=100)
    comments = models.TextField()
    status = models.CharField(max_length=1, choices=ACTIVITY_STATUSES)
    send_email = models.BooleanField(default=False)
    notes = models.JSONField()


    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'

class Request(BaseModel):
    title = models.CharField(max_length=50)
    description = models.TextField()
    group_id = models.CharField(max_length=10)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    category = models.CharField(max_length=50)
    status = models.CharField(max_length=1, choices=REQUEST_STATUSES)
