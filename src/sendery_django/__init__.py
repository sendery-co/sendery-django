"""Sendery integration for Django."""
from django.core.mail import EmailMultiAlternatives
import json
import uuid


class TemplateEmail(EmailMultiAlternatives):
    def __init__(self, *, to, template, data, locale=None, idempotency_key=None, **kwargs):
        super().__init__(to=[to], **kwargs)
        self.sendery_payload = json.loads(json.dumps({"template": template, "data": data, "locale": locale}, allow_nan=False))
        self.sendery_key = idempotency_key if idempotency_key is not None else str(uuid.uuid4())

    def message(self):
        # SMTP, console, file, and in-memory backends all request the MIME message.
        # The Sendery backend sends the template reference without rendering here.
        from django.conf import settings
        from sendery import Sendery
        signature = json.dumps(self.sendery_payload, sort_keys=True)
        if getattr(self, "_render_signature", None) != signature:
            rendered = Sendery(settings.SENDERY_API_KEY, getattr(settings, "SENDERY_URL", "https://sendery.co")).render(**self.sendery_payload)
            self.subject, self.body = rendered["subject"], rendered["text"]
            self.alternatives = [part for part in self.alternatives if part.mimetype != "text/html"]
            self.attach_alternative(rendered["html"], "text/html")
            self._render_signature = signature
        return super().message()

    def version(self, version):
        if type(version) is not int or version < 1:
            raise ValueError("Version must be a positive integer.")
        self.sendery_payload["version"] = version
        return self


def event(*, name, object_type, object_id, data, correlation_id=None, idempotency_key=None, language=None):
    """Prepare an event using the same project credentials as Django email."""
    from django.conf import settings
    from sendery import Sendery
    return Sendery(settings.SENDERY_API_KEY, getattr(settings, "SENDERY_URL", "https://sendery.co")).event(
        name=name, object_type=object_type, object_id=object_id, data=data,
        correlation_id=correlation_id, idempotency_key=idempotency_key, language=language,
    )


def define_event(name, definition):
    """Register an event using the configured project credentials."""
    from django.conf import settings
    from sendery import Sendery
    return Sendery(settings.SENDERY_API_KEY, getattr(settings, "SENDERY_URL", "https://sendery.co")).define_event(name, definition)
