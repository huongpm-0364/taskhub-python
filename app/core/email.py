import logging

logger = logging.getLogger("taskhub.email")


def send_email(*, to: str, subject: str, body: str) -> None:
    """Placeholder for real email delivery (SMTP, SES, Postmark, ...).

    This project has no email provider configured, so it just logs instead of actually
    sending anything. Swap the body of this function for a real provider call when one
    is available — callers don't need to change.
    """
    logger.info("Email to %s | subject=%r | body=%r", to, subject, body)
