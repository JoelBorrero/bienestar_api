from datetime import datetime

import pandas as pd
from django.db import models
from django_lifecycle import AFTER_CREATE, BEFORE_UPDATE, hook

from apps.utils.models import BaseModel
from apps.accounts.models import Activity, Group


class UploadedReport(BaseModel):
    file = models.FileField()
    result = models.JSONField()

    @hook(AFTER_CREATE)
    def on_create(self):
        group, created = Group.objects.get_or_create(name='Test', email='email@email.com')
        Activity.objects.create(
            name='name',
            description=str(self),
            group=group,
            date=datetime.now()
        )
        read_from_excel(self.file)

def read_from_excel(excel):
    keys = (
        'id',  # NO
        'created_at',  # Marca temporal
        'email',  # Dirección de correo electrónico
        'group',  # Nombre del grupo
        'responsible',  # Responsable(s)
        'name',  # Nombre del evento
        'description',  # Descripción del evento
        'start_date',  # Fecha y hora de inicio del evento
        'end_date',  # Fecha y hora de finalización del evento
        'category',  # Categoria
        'is_virtual',  # Tipo de evento
        'institutional',  # ¿Cual evento institucional?
        'bienestar',  # ¿Cual evento de Bienestar Universitario?
        'has_guests',  # ¿Posee invitados?
        'guests_info',  # Información de invitados
        'local_guests',  # ¿Cuantos invitados locales?
        'national_guests',  # ¿Cuantos invitados nacionales?
        'international_guests',  # ¿Cuantos invitados internacionales?
        'event_url',  # Link del evento
        'comments',  # COMENTARIOS
        'status',  # Estado
        'send_email',  # Enviar correo?
        'notes'  # Notas internas
    )
    data = pd.read_excel(excel, engine='openpyxl', sheet_name='Productos')
    # data = data.dropna(how='all')
    for i in range(len(data)):
        row = data.iloc[i]
        event_data = {'index': i}
        for index, key in enumerate(keys):
            event_data[key] = row[index]
        product, created = product_from_dict(event_data)
