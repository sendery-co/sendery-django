import pickle
import unittest
from unittest.mock import patch
from django.conf import settings
if not settings.configured:
    settings.configure(SECRET_KEY="test-only", ROOT_URLCONF=__name__, INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"], SENDERY_API_KEY="test", EMAIL_BACKEND="sendery_django.backend.EmailBackend", DEFAULT_FROM_EMAIL="hello@example.com")
import django
django.setup()
from django.urls import path
from django.http import HttpResponse
from django.test import override_settings
urlpatterns = [path("reset/<uidb64>/<token>/", lambda request, **kwargs: HttpResponse(), name="password_reset_confirm")]
from django.core.mail import EmailMessage
from sendery_django import TemplateEmail
from sendery_django.backend import EmailBackend


class BackendTests(unittest.TestCase):
    def test_queue_serialization_preserves_key_and_data(self):
        data = {"name": "Original"}
        email = TemplateEmail(to="alex@example.com", template="welcome", data=data)
        email.version(3)
        email.attach("invoice.pdf", b"PDF\x00bytes", "application/pdf")
        data["name"] = "Changed"
        restored = pickle.loads(pickle.dumps(email))
        with patch("sendery_django.backend.Sendery") as client:
            self.assertEqual(1, EmailBackend().send_messages([restored]))
            payload = client.return_value.send.call_args.kwargs
        self.assertEqual(__import__("base64").b64encode(b"PDF\x00bytes").decode(), payload["attachments"][0]["content"])
        self.assertEqual(email.sendery_key, payload["idempotency_key"])
        self.assertEqual(3, payload["version"])
        self.assertEqual("Original", payload["data"]["name"])

    def test_rejects_ordinary_emails_and_multiple_recipients(self):
        with self.assertRaises(ValueError):
            EmailBackend().send_messages([EmailMessage("subject", "body", to=["a@example.com"])])
        email = TemplateEmail(to="a@example.com", template="welcome", data={})
        email.to.append("b@example.com")
        with self.assertRaises(ValueError):
            EmailBackend().send_messages([email])

    def test_password_reset_keeps_django_token_and_url(self):
        from sendery_django.forms import SenderyPasswordResetForm
        from types import SimpleNamespace
        user = SimpleNamespace(get_username=lambda: "Alex")
        context = {"uid": "MTI", "token": "signed-token", "protocol": "https", "domain": "product.example", "user": user}
        with patch("sendery_django.forms.TemplateEmail") as message:
            SenderyPasswordResetForm().send_mail("subject", "body", context, "hello@example.com", "alex@example.com")
        self.assertEqual("https://product.example/reset/MTI/signed-token/", message.call_args.kwargs["data"]["action_url"])
        self.assertEqual("password-reset", message.call_args.kwargs["template"])
        message.return_value.send.assert_called_once()

    @override_settings(SENDERY_PASSWORD_RESET_TEMPLATE="account-recovery")
    def test_password_reset_uses_configured_template_and_preserves_url(self):
        from sendery_django.forms import SenderyPasswordResetForm
        from types import SimpleNamespace
        user = SimpleNamespace(get_username=lambda: "Alex")
        context = {"uid": "MTI", "token": "signed-token", "protocol": "https", "domain": "product.example", "user": user}
        with patch("sendery_django.backend.Sendery") as client:
            SenderyPasswordResetForm().send_mail("subject", "body", context, "hello@example.com", "alex@example.com")
            payload = client.return_value.send.call_args.kwargs
        self.assertEqual("account-recovery", payload["template"])
        self.assertEqual("alex@example.com", payload["to"])
        self.assertEqual({"name": "Alex", "action_url": "https://product.example/reset/MTI/signed-token/"}, payload["data"])
        client.return_value.send.assert_called_once()
