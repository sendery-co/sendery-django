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

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "sendery_django.backend.EmailBackend")
SENDERY_API_KEY = os.environ["SENDERY_API_KEY"]
```

## Development and staging

Use a **Sandbox** API key for development and staging. Sendery prevents email and workflow delivery from that key, even when the project is live. Production requires a **Live** key and live sending enabled on the project.

`TemplateEmail` respects Django’s `EMAIL_BACKEND` and explicit connections. SMTP, console, and in-memory backends receive the published Sendery subject, HTML, and text. Configure SMTP with Django’s usual `EMAIL_HOST`, `EMAIL_PORT`, and authentication settings; use a test destination in development. Rendering requires an API key. Rendering is limited to 10 requests per minute per workspace and 100 / 1,000 / 5,000 / 10,000 per calendar month on Free / Starter / Business / Scale or Enterprise. Render errors stop delivery. Events use the API independently of `EMAIL_BACKEND`.

## Send an email

Send a published template with `TemplateEmail`. Replace `your-template` with your published template’s key and `data` with its variables. Set the sender in your Sendery project.

When using the Sendery backend, `sendery_receipt` contains the email’s ID and status.

```python
from sendery_django import TemplateEmail

email = TemplateEmail(
    to="steven@example.com",
    template="your-template",
    data={"name": "Steven", "action_url": "https://example.com/start"},
)
email.send(fail_silently=False)
```

## Send a specific version

Choose a [published template version](https://sendery.co/en/docs/send-email#section-5) to keep sending it after newer versions are published. By default, Sendery uses the latest version.

```python
from sendery_django import TemplateEmail

email = TemplateEmail(
    to="steven@example.com",
    template="your-template",
    data={"name": "Steven", "action_url": "https://example.com/start"},
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
    to="steven@example.com",
    template="your-template",
    data={"name": "Steven", "action_url": "https://example.com/start"},
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
    to="steven@example.com",
    template="your-template",
    data={"name": "Steven", "action_url": "https://example.com/start"},
    idempotency_key="your-idempotency-key",
)
email.send(fail_silently=False)
```

## More

Learn how to [retry emails without duplicate sends](https://sendery.co/en/docs/idempotency).

## License

[MIT](LICENSE).

## Events and workflows

Send events such as account signups or orders from your app. Your team can use them to automate emails in Sendery, choosing the content, recipients, and timing. Available on all plans.

Start with [Connecting your application](https://sendery.co/en/docs/connect-events) to define the data Sendery can expect, then [send events](https://sendery.co/en/docs/send-events) as they happen. Define at least one email address field and include an address when sending events.

```python
from sendery_django import event

receipt = event(
    name="account.created", language="en", object_type="account", object_id="842",
    data={"email": "steven@example.com", "name": "Steven"},
).retry().send()
```

`language` selects a published template translation; omit it to use the template’s default.

Retries reuse the same event data and idempotency key. To retry across jobs or process restarts, supply and persist your own key. A successful response confirms that Sendery accepted the event. [Learn what you can automate with workflows](https://sendery.co/en/docs/build-workflow).
