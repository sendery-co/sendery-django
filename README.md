# Sendery — Django integration

Send template emails from Django with the Sendery SDK.

MIT licensed. Repository: https://github.com/sendery-co/sendery-django

Documentation: https://sendery.co/en/docs/django

## Install

```
pip install sendery-django
```

## Install

Django 5.2 / Python 3.10+

## Configure the email backend

Set EMAIL_BACKEND = "sendery_django.backend.EmailBackend" and SENDERY_API_KEY in settings, reading the key from your environment. This integration targets Django 5.2.

## Send a template email

Use TemplateEmail instead of an ordinary EmailMessage. Sending arbitrary HTML, attachments, CC/BCC, or multiple recipients is rejected. Keep fail_silently disabled when you need to handle failures.

## Password reset

Configure Django’s PasswordResetView with form_class=SenderyPasswordResetForm from sendery_django.forms. The form uses Django’s own token and password_reset_confirm route. Publish a password-reset template with name and action_url variables.

## Queued work

Pass a stable idempotency_key and freeze the variables in a Celery or other application job. The backend does not silently add another retry loop.

## Configuration example

```
EMAIL_BACKEND = "sendery_django.backend.EmailBackend"
SENDERY_API_KEY = os.environ["SENDERY_API_KEY"]
```

## Example

```
from sendery_django import TemplateEmail

email = TemplateEmail(
    to=user.email, template="welcome", data={"name": user.get_username()},
    idempotency_key=f"welcome-{user.pk}",
)
email.send()
```

## Retries and queues

Reuse a prepared email for retries. New requests receive new keys; when reconstructing a request in another process, supply the original key and unchanged data. Keep API keys server-side. Framework mailers send Sendery templates, not arbitrary HTML or attachments.
