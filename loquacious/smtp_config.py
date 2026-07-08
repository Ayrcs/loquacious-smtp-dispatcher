import os
from pathlib import Path


class SMTPConfig:
    def __init__(self):
        self.contacts_path = Path("contacts")
        self.emails_path = Path("emails")
        self.smtp_server = None
        self.smtp_port = 587
        self.smtp_username = None
        self.smtp_password = None
        self.smtp_timeout = 30
        self.use_tls = True

        self.repeat_send_email: int = 1
        self.delay_seconds: float = 0.1

        self.sender_email = None
        self.sender_name = ""
        self.subject = None
        self.custom_headers = {}
        self.dry_run = False

    def init(self, kwargs=None):
        kwargs = kwargs or {}

        defaults = {
            "contacts_path": os.getenv("LOQUACIOUS_CONTACTS_PATH"),
            "emails_path": os.getenv("LOQUACIOUS_EMAILS_PATH"),
            "smtp_server": os.getenv("LOQUACIOUS_SMTP_SERVER"),
            "smtp_port": os.getenv("LOQUACIOUS_SMTP_PORT"),
            "smtp_username": os.getenv("LOQUACIOUS_SMTP_USERNAME"),
            "smtp_password": os.getenv("LOQUACIOUS_SMTP_PASSWORD"),
            "smtp_timeout": os.getenv("LOQUACIOUS_SMTP_TIMEOUT"),
            "sender_email": os.getenv("LOQUACIOUS_SENDER_EMAIL"),
            "sender_name": os.getenv("LOQUACIOUS_SENDER_NAME"),
            "subject": os.getenv("LOQUACIOUS_SUBJECT"),
            "repeat_send_email": os.getenv("LOQUACIOUS_REPEAT_SEND_EMAIL"),
            "delay_seconds": os.getenv("LOQUACIOUS_DELAY_SECONDS"),
        }

        for key, value in {**defaults, **kwargs}.items():
            if value is not None and value != "":
                setattr(self, key, value)

        self.contacts_path = Path(self.contacts_path)
        self.emails_path = Path(self.emails_path)
        self.smtp_port = int(self.smtp_port)
        self.smtp_timeout = int(self.smtp_timeout)
        self.repeat_send_email = int(self.repeat_send_email)
        self.delay_seconds = float(self.delay_seconds)
        self.use_tls = self._as_bool(self.use_tls)
        self.dry_run = self._as_bool(self.dry_run)

        if not self.sender_email and self.smtp_username:
            self.sender_email = self.smtp_username

    def validate(self):
        if not self.contacts_path.exists():
            raise FileNotFoundError(f"Contacts path does not exist: {self.contacts_path}")
        if not self.emails_path.exists():
            raise FileNotFoundError(f"Emails path does not exist: {self.emails_path}")
        if not self.sender_email:
            raise ValueError("A sender email is required")
        if not self.dry_run and not self.smtp_server:
            raise ValueError("An SMTP server is required unless --dry-run is enabled")

    @staticmethod
    def _as_bool(value):
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "on"}
