import argparse
import csv
import re
import time
from dataclasses import dataclass
from pathlib import Path

from loquacious.smtp_bridge import SMTPBridge
from loquacious.smtp_config import SMTPConfig
from loquacious.smtp_contact import SMTPContact
from loquacious.smtp_message import SMTPMessage


@dataclass
class SMTPTemplate:
    subject: str
    html_body: str
    source: Path


class SMTPApp:
    def __init__(self):
        self.config: SMTPConfig = SMTPConfig()
        self.smtp_bridge: SMTPBridge | None = None

    def run(self, argv=None):
        args = self._parse_args(argv)
        self.config.init(vars(args))
        self.config.validate()
        self.smtp_bridge = SMTPBridge(self.config)

        contacts = self.load_contacts()
        templates = self.load_messages()
        sender = SMTPContact(
            name=self.config.sender_name,
            email=self.config.sender_email,
        )

        print(f"Loaded {len(contacts)} contact(s)")
        print(f"Loaded {len(templates)} email template(s)")

        for template in templates:
            for contact in contacts:
                for send_number in range(self.config.repeat_send_email):
                    message = self.build_message(sender, contact, template)
                    print(
                        f"Sending {template.source.name} to {contact.email} "
                        f"({send_number + 1}/{self.config.repeat_send_email})"
                    )
                    self.smtp_bridge.send_mail(message)
                    time.sleep(self.config.delay_seconds)

    def load_contacts(self):
        contacts = []

        for path in self._find_files(self.config.contacts_path, "*.csv"):
            with path.open(newline="", encoding="utf-8-sig") as contacts_file:
                reader = csv.DictReader(contacts_file)
                for row in reader:
                    contacts.append(SMTPContact.from_csv_row(row))

        if not contacts:
            raise ValueError(f"No contacts found in {self.config.contacts_path}")

        return contacts

    def load_messages(self):
        templates = []

        for path in self._find_files(self.config.emails_path, "*.html"):
            subject = self.config.subject or path.stem.replace("_", " ").strip()
            templates.append(
                SMTPTemplate(
                    subject=subject,
                    html_body=path.read_text(encoding="utf-8"),
                    source=path,
                )
            )

        if not templates:
            raise ValueError(f"No HTML email templates found in {self.config.emails_path}")

        return templates

    def build_message(self, sender, contact, template):
        data = {"sender_name": sender.name, "sender_email": sender.email, **contact.data}
        subject = self._render(template.subject, data)
        html_body = self._render(template.html_body, data)
        headers = {
            name: self._render(value, data)
            for name, value in self.config.custom_headers.items()
        }

        return SMTPMessage(
            sender=sender,
            recipient=contact,
            subject=subject,
            html_body=html_body,
            headers=headers,
        )

    @staticmethod
    def _find_files(path, pattern):
        if path.is_file():
            return [path]
        return sorted(path.glob(pattern))

    @staticmethod
    def _render(template, data):
        def replace(match):
            return data.get(match.group(1), "")

        return re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", replace, template)

    def _parse_args(self, argv):
        parser = argparse.ArgumentParser(
            description="Send HTML emails to contacts through SMTP."
        )
        parser.add_argument("--contacts-path")
        parser.add_argument("--emails-path")
        parser.add_argument("--smtp-server")
        parser.add_argument("--smtp-port", type=int)
        parser.add_argument("--smtp-username")
        parser.add_argument("--smtp-password")
        parser.add_argument("--smtp-timeout", type=int)
        parser.add_argument("--sender-email")
        parser.add_argument("--sender-name")
        parser.add_argument("--subject")
        parser.add_argument("--repeat-send-email", type=int)
        parser.add_argument("--delay-seconds", type=float)
        parser.add_argument("--header", action="append", default=[])
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--no-tls", dest="use_tls", action="store_false")
        parser.set_defaults(use_tls=True)

        args = parser.parse_args(argv)
        args.custom_headers = self._parse_headers(args.header)
        del args.header

        return args

    @staticmethod
    def _parse_headers(headers):
        parsed = {}
        for header in headers:
            if "=" not in header:
                raise ValueError(f"Invalid header format: {header}. Use Name=Value.")
            name, value = header.split("=", 1)
            if not name.strip():
                raise ValueError(f"Invalid header format: {header}. Header name is empty.")
            parsed[name.strip()] = value.strip()
        return parsed
