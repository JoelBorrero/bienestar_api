from django.db import models
from django_lifecycle import AFTER_CREATE, hook

from apps.analyzer.tasks import read_from_excel
from apps.utils.models import BaseModel


class UploadedReport(BaseModel):
    file = models.FileField()
    result = models.JSONField(blank=True, null=True)

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"

    @hook(AFTER_CREATE)
    def on_create(self):
        self.result = {"result": read_from_excel(self.file)}
        self.save()
