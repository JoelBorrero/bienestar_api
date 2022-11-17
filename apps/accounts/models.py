from django.contrib.gis.db import models
from django_lifecycle import AFTER_CREATE, BEFORE_UPDATE, hook

from apps.utils.constants import ACTIVITY_CATEGORIES, ACTIVITY_STATUSES
from apps.utils.models import BaseModel, BaseModelUser
from apps.utils.redis import client as redis


class Account(BaseModelUser):
    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"

    def __str__(self):
        return self.first_name if self.first_name else self.username

    @hook(AFTER_CREATE)
    def on_create(self):
        if redis.get_json("setup").get("disable_user_when_register"):
            self.disable()
        self.set_raw_password()
        self.email = self.username
        self.save(update_fields=["email"])

    @hook(BEFORE_UPDATE)
    def on_update(self):
        self.set_raw_password()


class Activity(BaseModel):
    ext_id = models.CharField("Id Uninorte", max_length=15, unique=True)
    email = models.CharField(max_length=50)
    group = models.ForeignKey("Group", on_delete=models.CASCADE)
    responsible = models.CharField("Responsable", max_length=501)
    name = models.CharField("Nombre del evento", max_length=502)
    description = models.TextField("Descripción")
    start_date = models.DateTimeField("Fecha de inicio")
    end_date = models.DateTimeField("Fecha de finalización")
    category = models.CharField("Categoría", max_length=3, choices=ACTIVITY_CATEGORIES)
    is_virtual = models.BooleanField("Es virtual")
    institutional = models.CharField("Institucional", max_length=51, blank=True)
    bienestar = models.CharField(max_length=52, blank=True)
    has_guests = models.BooleanField("Posee invitados")
    guests_info = models.CharField(
        "Información de invitados", max_length=503, blank=True
    )
    local_guests = models.PositiveSmallIntegerField("Invitados locales", default=0)
    national_guests = models.PositiveSmallIntegerField(
        "Invitados nacionales", default=0
    )
    international_guests = models.PositiveSmallIntegerField(
        "Invitados internacionales", default=0
    )
    event_url = models.CharField("URL del evento", max_length=1804, blank=True)
    comments = models.TextField("Comentarios")
    status = models.CharField(
        "Estado", max_length=1, choices=ACTIVITY_STATUSES, default="p"
    )
    send_email = models.BooleanField("Enviar email", default=False)
    notes = models.JSONField("Notas")

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"

    def __str__(self) -> str:
        return f"{self.name} - {self.pk}"


class Group(Account):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"

    def __str__(self) -> str:
        return self.name
