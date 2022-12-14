import os
import pytz


ACTIVITY_CATEGORIES = (
    ("cap", "Capacitaciones"),
    ("crs", "Campaña en redes sociales"),
    ("eab", "Evento abierto"),
    ("ebu", "Eventos de Bienestar Universitario"),
    ("ema", "Eventos masivos"),
    ("int", "Actividades internas"),
    ("pub", "Publicaciones"),
    ("nan", "No encontrado"),
)

ACTIVITY_STATUSES = (
    ("a", "Aprobado"),
    ("d", "Denegado"),
    ("i", "Aprobado - Importante"),
    ("p", "Pendiente"),
    ("t", "Terminado"),
    ("n", "No encontrado"),
)

TIMEZONE = pytz.timezone(os.environ.get("TZ", "America/Bogota"))
