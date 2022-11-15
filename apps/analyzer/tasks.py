from datetime import datetime, timedelta

import nltk
import pandas as pd
from celery import shared_task
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

from .services import get_categories_coverage
from apps.utils.choices import GROUP
from apps.utils.constants import TIMEZONE
from apps.utils.constants import ACTIVITY_CATEGORIES, ACTIVITY_STATUSES
from apps.accounts.models import Activity, Group


def read_from_excel(excel):
    def get_category(category_name):
        for key, category in ACTIVITY_CATEGORIES:
            if category.lower() == category_name.lower():
                return key
        return "nan"

    def get_status(status_name):
        for key, status in ACTIVITY_STATUSES:
            if status.lower() == status_name.lower():
                return key
        return "n"

    keys = (
        ("id", "NO"),
        ("created_at", "Marca temporal"),
        ("email", "Dirección de correo electrónico"),
        ("group", "Nombre del grupo"),
        ("responsible", "Responsable(s)"),
        ("name", "Nombre del evento"),
        ("description", "Descripción del evento"),
        ("start_date", "Fecha y hora de inicio del evento"),
        ("end_date", "Fecha y hora de finalización del evento"),
        ("category", "Categoria"),
        ("is_virtual", "Tipo de evento"),
        ("institutional", "¿Cual evento institucional?"),
        ("bienestar", "¿Cual evento de Bienestar Universitario?"),
        ("has_guests", "¿Posee invitados?"),
        ("guests_info", "Información de invitados"),
        ("local_guests", "¿Cuantos invitados locales?"),
        ("national_guests", "¿Cuantos invitados nacionales?"),
        ("international_guests", "¿Cuantos invitados internacionales?"),
        ("event_url", "Link del evento"),
        ("comments", "COMENTARIOS"),
        ("status", "Estado"),
        ("send_email", "Enviar correo?\n"),
        ("notes", "Notas importantes (Internas) ORIETA"),
        ("notes_2", "Notas Luz"),
    )
    data = pd.read_excel(excel, engine="openpyxl")
    res = {"created": [], "updated": []}
    for i in range(len(data)):
        row = data.iloc[i]
        row = row.dropna()
        event = {}
        for key, column_name in keys:
            value = row.get(column_name)
            if value:
                event[key] = value
        if type(event["created_at"]) is not datetime:
            event["created_at"] = event["created_at"].to_pydatetime()
        group, created = Group.objects.get_or_create(
            name=event["group"],
            defaults={
                "username": event["email"],
                "role": GROUP,
                "first_name": event["group"],
            },
        )
        if created:
            res["created"].append(f"{group.name} ({group.pk})")
            group.set_password("uninorte")
            group.save()
        event["group"] = group
        for key in ["start_date", "end_date"]:
            if type(event[key]) is not datetime:
                if int(event[key].split("/")[1]) > 12:
                    format = "%m/%d/%Y %H:%M:%S"
                else:
                    format = "%d/%m/%Y %H:%M:%S"
                event[key] = event[key].replace(".", ":")  # It's for errors on typing
                event[key] = datetime.strptime(event[key], format)
                event[key] = event[key].replace(tzinfo=TIMEZONE)
        event["category"] = get_category(event["category"])
        event["is_virtual"] = event["is_virtual"].lower() == "virtual"
        event["has_guests"] = event.get("has_guests", "").lower() == "si"
        event["status"] = get_status(event.get("status", ""))
        event["send_email"] = event.get("send_email", "").lower() == "si"
        event[
            "notes"
        ] = f'Notas Orieta:/n{event.get("notes")}/nNotas Luz:/n{event.get("notes_2")}'
        if "notes_2" in event:
            event.pop("notes_2")
        ext_id = event.pop("id")
        activity, created = Activity.objects.update_or_create(
            ext_id=ext_id, defaults=event
        )
        res["created" if created else "updated"].append(
            f"{activity.ext_id} ({activity.pk})"
        )
    return res


@shared_task
def load_statistics(start_date=None, end_date=None):
    if type(start_date) is str:
        start_date = datetime.strptime(f"{start_date} 23:59", "%Y-%m-%d %H:%M").replace(
            tzinfo=TIMEZONE
        )
    if type(end_date) is str:
        end_date = datetime.strptime(f"{end_date} 23:59", "%Y-%m-%d %H:%M").replace(
            tzinfo=TIMEZONE
        )
    if not end_date:
        end_date = datetime.now(TIMEZONE)
    if not start_date:
        start_date = end_date - timedelta(days=30, hours=23, minutes=59)
    coverage_result = get_categories_coverage(start_date, end_date)
    result = {
        "start_date": start_date,
        "end_date": end_date,
        "total": coverage_result["total"],
        "coverage": coverage_result["data"],
    }
    return result


def common_words_activities_months():
    dates = []
    for activity in Activity.objects.order_by("start_date"):
        month = activity.start_date.month
        year = activity.start_date.year
        date = {"month": month, "year": year}
        if date not in dates:
            dates.append(date)

    for date in dates:
        activities = Activity.objects.filter(
            start_date__year=date["year"], start_date__month=date["month"]
        )
        fdist = common_words_activities(activities)
        date["fdist"] = fdist

    return dates


def common_words_activities():
    activities = Activity.objects.all()
    text = ""
    for activity in activities:
        text += " " + activity.name + " " + activity.description

    tokens_lower = [word.lower() for word in wordpunct_tokenize(text)]
    stopw = stopwords.words("spanish")
    punctuation = [
        ".",
        "[",
        "]",
        ",",
        ";",
        "",
        ")",
        "),",
        " ",
        "(",
        "?",
        "¿",
        "-",
        ":",
        '"',
        "/",
    ]
    stopw.extend(punctuation)
    words = [token for token in tokens_lower if token not in stopw]

    snowball_stemmer = SnowballStemmer("spanish")
    stemmers = [snowball_stemmer.stem(word) for word in words]
    final = [stem for stem in stemmers if stem.isalpha() and len(stem) > 1]
    fdist_stemming = nltk.FreqDist(final)

    # fdist = nltk.FreqDist(words) # Frequency of words without stemming
    return fdist_stemming
