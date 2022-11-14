from django.db import models

from apps.accounts.models import Account
from apps.utils.models import BaseModel


class Record(BaseModel):
    promoter = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="promoter"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    zone = models.ForeignKey("Zone", on_delete=models.CASCADE)
    was_supervised = models.BooleanField()
    supervisor = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="supervisor",
        blank=True,
        null=True,
    )
    wake_up_calls = models.PositiveSmallIntegerField(blank=True, null=True)
    people_called = models.PositiveSmallIntegerField(blank=True, null=True)
    promoter_notes = models.TextField(blank=True, null=True)
    supervisor_wake_up_calls = models.PositiveSmallIntegerField(blank=True, null=True)
    supervisor_notes = models.TextField(blank=True, null=True)
    is_signed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Registro de hora"
        verbose_name_plural = "Registros de horas"


class Zone(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"

    def __str__(self) -> str:
        return self.name
