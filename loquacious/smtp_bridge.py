import smtplib

from loquacious.smtp_message import SMTPMessage


class SMTPBridge:
    def __init__(self, config):
        self.config = config

    def send_mail(self, message: SMTPMessage):
        email_message = message.to_email_message()

        if self.config.dry_run:
            print(
                f"[dry-run] {message.sender.email} -> {message.recipient.email} "
                f"subject={message.subject!r}"
            )
            return

        with smtplib.SMTP(
            self.config.smtp_server,
            self.config.smtp_port,
            timeout=self.config.smtp_timeout,
        ) as smtp:
            if self.config.use_tls:
                smtp.starttls()

            if self.config.smtp_username and self.config.smtp_password:
                smtp.login(self.config.smtp_username, self.config.smtp_password)

            smtp.send_message(email_message)
