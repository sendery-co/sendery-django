from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from sendery import Sendery, SenderyError, attachment
from . import TemplateEmail


class EmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        client = Sendery(settings.SENDERY_API_KEY, getattr(settings, "SENDERY_URL", "https://sendery.co"))
        sent = 0
        for message in email_messages or []:
            if not isinstance(message, TemplateEmail) or len(message.to) != 1 or message.cc or message.bcc:
                raise ValueError("Use TemplateEmail with exactly one recipient and no CC or BCC.")
            attachments = []
            for item in message.attachments:
                if not isinstance(item, tuple) or len(item) != 3:
                    raise ValueError("Use attach(filename, content, mimetype); inline/MIME attachments are not supported.")
                filename, content, mimetype = item
                if isinstance(content, str):
                    content = content.encode("utf-8")
                attachments.append(attachment(filename, content, mimetype))
            try:
                message.sendery_receipt = client.send(to=message.to[0], **message.sendery_payload, idempotency_key=message.sendery_key, attachments=attachments)
                sent += 1
            except SenderyError:
                if not self.fail_silently:
                    raise
        return sent
