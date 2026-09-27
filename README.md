# Sendery for Django

Send Sendery templates through Django’s email backend.

[Documentation](https://sendery.co/en/docs/django) · [API reference](https://sendery.co/en/docs/send-email) · [Changelog](CHANGELOG.md)

## Requirements

Django 5.2 and Python 3.10+.

## Install

```bash
pip install sendery-django
```

## Configure the backend

Publish a `welcome` template with `name` and `action_url` variables, and create a [project API key](https://sendery.co/en/docs/authentication). Store it as `SENDERY_API_KEY` on your server. Add the backend and key to your Django settings.

```python
# settings.py
import os

EMAIL_BACKEND = "sendery_django.backend.EmailBackend"
SENDERY_API_KEY = os.environ["SENDERY_API_KEY"]
```

## Send an email

Use `TemplateEmail` with one recipient. Its `sendery_receipt` contains the accepted email’s ID and status. Ordinary `EmailMessage` objects, attachments, and `cc` or `bcc` recipients are not supported. Set the sender in your Sendery project.

```python
from sendery_django import TemplateEmail

email = TemplateEmail(
    to="alex@example.com",
    template="welcome",
    data={"name": "Alex", "action_url": "https://example.com/start"},
)
email.send(fail_silently=False)

print(email.sendery_receipt["id"])
```

## Password resets

Publish a `password-reset` template with `name` and `action_url`. Use `SenderyPasswordResetForm` with Django’s authentication views. Add these routes to your `urlpatterns` and provide Django’s standard password-reset HTML pages under `templates/registration/`. If the routes already exist, change only the reset view’s `form_class`.

```python
# urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from sendery_django.forms import SenderyPasswordResetForm

urlpatterns = [
    path("password-reset/", auth_views.PasswordResetView.as_view(
        form_class=SenderyPasswordResetForm,
    ), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),
]
```

## Retry a send

Keep `fail_silently=False` to receive [`SenderyError`](https://sendery.co/en/docs/python) on API failures. The backend makes one attempt. In a [background task](https://sendery.co/en/docs/queues), save the recipient, variables, and `idempotency_key` before sending and reuse them for retries.

```python
# Use the same saved recipient, variables, and event key on every attempt.
email = TemplateEmail(
    to="alex@example.com",
    template="welcome",
    data={"name": "Alex", "action_url": "https://example.com/start"},
    idempotency_key="welcome-123",
)
email.send(fail_silently=False)
```

## More

See [idempotency and retries](https://sendery.co/en/docs/idempotency) for retry conditions, delays, and reusing a key across attempts.

## License

[MIT](LICENSE).
