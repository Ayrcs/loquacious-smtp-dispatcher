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
        message["From"] = formataddr((self.sender.name, self.sender.email))
        message["To"] = formataddr((self.recipient.name, self.recipient.email))
        message["Subject"] = self.subject
        message["Message-ID"] = self.header_id

        for name, value in self.headers.items():
            if name.lower() in {"from", "to", "subject", "message-id"}:
                continue
            message[name] = value

        message.set_content("This email requires an HTML-compatible email client.")
        message.add_alternative(self.html_body, subtype="html")

        return message
