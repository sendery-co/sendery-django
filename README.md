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

Create a [project API key](https://sendery.co/en/docs/authentication), store it as `SENDERY_API_KEY`, and add the backend to `settings.py`.

```python
# settings.py
import os

EMAIL_BACKEND = "sendery_django.backend.EmailBackend"
SENDERY_API_KEY = os.environ["SENDERY_API_KEY"]
```

## Send an email

Send a published template with `TemplateEmail`. Replace `your-template` with your published template’s key and `data` with its variables. Set the sender in your Sendery project.

After sending, `sendery_receipt` contains the email’s ID and status.

```python
from sendery_django import TemplateEmail

email = TemplateEmail(
    to="alex@example.com",
    template="your-template",
    data={"name": "Alex", "action_url": "https://example.com/start"},
)
email.send(fail_silently=False)

print(email.sendery_receipt["id"])
```

## Send a specific version

Choose a [published template version](https://sendery.co/en/docs/send-email#section-5) to keep sending it after newer versions are published. By default, Sendery uses the latest version.

```python
from sendery_django import TemplateEmail

email = TemplateEmail(
    to="alex@example.com",
    template="your-template",
    data={"name": "Alex", "action_url": "https://example.com/start"},
).version(3)

email.send(fail_silently=False)
```

## Attachments

Attach files to `TemplateEmail` with Django’s `attach()` method.

Send up to 10 files totaling 5 MB. See the [attachment reference](https://sendery.co/en/docs/send-email#section-6) for supported formats and limits.

```python
from pathlib import Path
from sendery_django import TemplateEmail

email = TemplateEmail(
    to="alex@example.com",
    template="your-template",
    data={"name": "Alex", "action_url": "https://example.com/start"},
    idempotency_key="your-idempotency-key",
)
email.attach("document.pdf", Path("document.pdf").read_bytes(), "application/pdf")
email.send(fail_silently=False)
```

## Password resets

Set `SENDERY_PASSWORD_RESET_TEMPLATE` to your published template’s key, and use `SenderyPasswordResetForm` on your reset view. The form supplies `name` and Django’s reset link as `action_url`.

If you already have password-reset routes, change only the form. Keep your existing confirmation pages.

```python
# settings.py
SENDERY_PASSWORD_RESET_TEMPLATE = "your-reset-template"

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

A failed send raises [`SenderyError`](https://sendery.co/en/docs/python). In a [background task](https://sendery.co/en/docs/queues), retry temporary failures with the same email data and `idempotency_key`. Keep `fail_silently=False` so your task runner can detect the failure.

```python
# Use the same saved recipient, variables, and event key on every attempt.
email = TemplateEmail(
    to="alex@example.com",
    template="your-template",
    data={"name": "Alex", "action_url": "https://example.com/start"},
    idempotency_key="your-idempotency-key",
)
email.send(fail_silently=False)
```

## More

Learn how to [retry emails without duplicate sends](https://sendery.co/en/docs/idempotency).

## License

[MIT](LICENSE).
