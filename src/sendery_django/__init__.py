"""Sendery integration for Django."""
from django.core.mail import EmailMessage
import json
import uuid


class TemplateEmail(EmailMessage):
    def __init__(self, *, to, template, data, locale=None, idempotency_key=None, **kwargs):
        super().__init__(to=[to], **kwargs)
        self.sendery_payload = json.loads(json.dumps({"template": template, "data": data, "locale": locale}, allow_nan=False))
        self.sendery_key = idempotency_key if idempotency_key is not None else str(uuid.uuid4())
