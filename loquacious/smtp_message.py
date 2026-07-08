from email.message import EmailMessage
from email.utils import formataddr, make_msgid

from loquacious.smtp_contact import SMTPContact


class SMTPMessage:
    def __init__(
        self,
        sender: SMTPContact,
        recipient: SMTPContact,
        subject: str,
        html_body: str,
        headers: dict | None = None,
    ):
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.html_body = html_body
        self.headers = headers or {}
        self.header_id = make_msgid(domain=sender.domain)

    def to_email_message(self):
        message = EmailMessage()
        self._set_header(message, "From", formataddr((self.sender.name, self.sender.email)))
        self._set_header(message, "To", formataddr((self.recipient.name, self.recipient.email)))
        self._set_header(message, "Subject", self.subject)
        self._set_header(message, "Message-ID", self.header_id)

        for name, value in self.headers.items():
            if name.lower() in {"to", "subject"}:
                continue

            self._set_header(message, name, value)

        message.set_content("This email requires an HTML-compatible email client.")
        message.add_alternative(self.html_body, subtype="html")

        return message

    @staticmethod
    def _set_header(message, name, value):
        if name in message:
            message.replace_header(name, value)
        else:
            message[name] = value
