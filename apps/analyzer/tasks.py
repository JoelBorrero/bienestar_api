from datetime import datetime, timedelta

import nltk
import pandas as pd
import numpy as np
from celery import shared_task
from nltk import wordpunct_tokenize, word_tokenize
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


def get_dates_range(start_date, end_date):
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
        start_date = end_date - timedelta(days=180, hours=23, minutes=59)
    return start_date, end_date


@shared_task
def load_statistics(start_date=None, end_date=None):
    start_date, end_date = get_dates_range(start_date, end_date)
    result = get_categories_coverage(start_date, end_date)
    return result


def common_words_activities_months(start_date=None, end_date=None):
    start_date, end_date = get_dates_range(start_date, end_date)
    activities = Activity.objects.filter(
        start_date__gte=start_date, end_date__lte=end_date
    ).order_by("start_date")
    dates = []
    for activity in activities:
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


def common_words_activities(activities):
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

    do_stemming = False
    if do_stemming:
        snowball_stemmer = SnowballStemmer("spanish")
        stemmers = [snowball_stemmer.stem(word) for word in words]
        final = [stem for stem in stemmers if stem.isalpha() and len(stem) > 1]
        fdist = nltk.FreqDist(final)
    else:
        fdist = nltk.FreqDist(words)  # Frequency of words without stemming
    return fdist


def processing_main():
    """Obtener todos las palabras claves que se repitan mas de 10 veces de los titulos de los articulos"""
    dict_verbs = {}
    filter_stopwords = stopwords.words('spanish')

    data = pd.DataFrame(list(Activity.objects.all().values('name', 'start_date')))
    data["name"] = data["name"].str.lower()
    data["name"] = (
        data["name"]
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    data["name"] = data["name"].str.replace("s ", " ")
    data["name"] = data["name"].str.replace("es ", " ")
    data["name"] = data["name"].str.replace("as ", " ")
    data["name"] = data["name"].str.replace("os ", " ")

    for i in range(len(data)):
        row = data.iloc[i]
        row = row.dropna()
        title = row['name']
        date = row['start_date']
        tokens = word_tokenize(title)
        for token in tokens:
            if token in dict_verbs:
                if date in dict_verbs[token]:
                    dict_verbs[token][date] += 1
                else:
                    dict_verbs[token][date] = 1
            else:
                dict_verbs[token] = {}
    for key in list(dict_verbs.keys()):
        if len(dict_verbs[key]) < 10:
            del dict_verbs[key]
        if key in filter_stopwords:
            try:
                dict_verbs.pop(key)
            except:
                pass
        if len(key) < 3:
            try:
                dict_verbs.pop(key)
            except:
                pass

    dict_for_month = {}
    for key in dict_verbs:
        for date in dict_verbs[key]:
            try:
                month = date.month
            except:
                continue
            if month in dict_for_month:
                if key in dict_for_month[month]:
                    dict_for_month[month][key] += dict_verbs[key][date]
                else:
                    dict_for_month[month][key] = dict_verbs[key][date]
            else:
                dict_for_month[month] = {}
                dict_for_month[month][key] = dict_verbs[key][date]
    return dict_for_month


def processing_date():
    """Obtener todos las palabras claves que se repitan mas de 10 veces de los titulos de los articulos"""
    dict_verbs = {}
    filter_stopwords = stopwords.words("spanish")

    data = pd.DataFrame(list(Activity.objects.all().values('name', 'start_date')))
    data["name"] = data["name"].str.lower()
    data["name"] = (
        data["name"]
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    data["name"] = data["name"].str.replace("s ", " ")
    data["name"] = data["name"].str.replace("es ", " ")
    data["name"] = data["name"].str.replace("as ", " ")
    data["name"] = data["name"].str.replace("os ", " ")

    for i in range(len(data)):
        row = data.iloc[i]
        row = row.dropna()
        title = row["name"]
        date = row["start_date"]
        tokens = word_tokenize(title)
        for token in tokens:
            if token not in filter_stopwords:
                if token not in dict_verbs:
                    dict_verbs[token] = []
                dict_verbs[token].append(date)

    for key in list(dict_verbs.keys()):
        if len(dict_verbs[key]) < 20:
            del dict_verbs[key]
        if key in filter_stopwords:
            try:
                dict_verbs.pop(key)
            except:
                pass
        if len(key) < 3:
            try:
                dict_verbs.pop(key)
            except:
                pass

    #ordenar la data por fechas
    for key in dict_verbs:
        dict_verbs[key] = sorted(dict_verbs[key])

    return dict_verbs


def generate_color():
    return f"rgb({np.random.choice(range(256))}, {np.random.choice(range(256))}, {np.random.choice(range(256))})"


def graph_data_common_words_months(month, amount):
    amount = int(amount) if amount else 5
    month = month if month else datetime.now(TIMEZONE).month
    activities = Activity.objects.filter(start_date__month=month)
    words_data = common_words_activities(activities).most_common(amount)

    labels = []
    data = []
    for d in words_data:
        labels.append(d[0])
        data.append(d[1])

    return {
        "labels": labels,
        "datasets": [{
            "label": "Palabra",
            "data": data,
            "backgroundColor": [generate_color() for _ in range(len(data))],
            "borderColor": [generate_color() for _ in range(len(data))],
            "tension": 0.4,
            "fill": True,
            "pointStyle": 'rect',
            "pointBorderColor": 'blue',
            "pointBackgroundColor": '#fff',
            "showLine": True
        }]
    }


def graph_data_pie_chart_type():
    virtual_activities = Activity.objects.filter(is_virtual=True).count()
    on_site_activities = Activity.objects.filter(is_virtual=False).count()
    labels = ["Virtual", "Presencial"]
    datasets = [
        {
            "label": "Tipo de actividad",
            "data": [virtual_activities, on_site_activities],
            "backgroundColor": ["#4bb2dd", "#c95355"],
            "borderColor": ["#fff", "#fff"],
            "tension": 0.4,
            "fill": True,
            "pointStyle": 'rect',
            "pointBorderColor": 'blue',
            "pointBackgroundColor": '#fff',
            "showLine": True
        }
    ]
    return {"labels": labels, "datasets": datasets}


def graph_data_categories_month(month):
    labels = [category[1] for category in ACTIVITY_CATEGORIES]
    categories = [category[0] for category in ACTIVITY_CATEGORIES]
    data = []
    for category in categories:
        count = Activity.objects.filter(start_date__month=month, category=category).count()
        data.append(count)

    return {
        "labels": labels,
        "datasets": [{
            "label": "Categoría",
            "data": data,
            "backgroundColor": [generate_color() for _ in range(len(categories))],
            "borderColor": [generate_color() for _ in range(len(categories))],
            "tension": 0.4,
            "fill": True,
            "pointStyle": 'rect',
            "pointBorderColor": 'blue',
            "pointBackgroundColor": '#fff',
            "showLine": True
        }]
    }
