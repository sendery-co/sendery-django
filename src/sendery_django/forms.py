from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse
from . import TemplateEmail


class SenderyPasswordResetForm(PasswordResetForm):
    template_key = "password-reset"

    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        path = reverse("password_reset_confirm", kwargs={"uidb64": context["uid"], "token": context["token"]})
        url = f"{context['protocol']}://{context['domain']}{path}"
        template = getattr(settings, "SENDERY_PASSWORD_RESET_TEMPLATE", self.template_key)
        TemplateEmail(to=to_email, template=template, data={"name": context["user"].get_username(), "action_url": url}, from_email=from_email).send()
