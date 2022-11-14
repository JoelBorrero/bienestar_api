from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template

from apps.utils.redis import client as redis


def send_email(subject: str, to_email: str, template: str, context: dict):
    setup = redis.get_json("setup")
    settings.EMAIL_HOST = setup.get("email_host")
    settings.EMAIL_HOST_USER = setup.get("email_host_user")
    settings.EMAIL_HOST_PASSWORD = setup.get("email_host_password")

    template = Template(template)
    # template = get_template(template)
    context = Context(context)
    html_template = template.render(context)
    msg = EmailMultiAlternatives(
        subject, subject, setup.get("from_email"), to=[to_email]
    )
    msg.attach_alternative(html_template, "text/html")
    res = msg.send()
    return str(res)
