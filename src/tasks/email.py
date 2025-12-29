"""src/tasks/email.py."""

import logging
import smtplib
from email.message import EmailMessage

from src.config import settings
from src.celery import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="send_email_task")
def send_email_task(email_to: str, subject: str, body: str):
    """
    Celery task for sending email.
    """
    logger.info("Starting email sending task to: %s", email_to)

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_FROM
    msg["To"] = email_to

    try:
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_STARTTLS:
                server.starttls()

            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)

            logger.info("Email successfully sent to %s", email_to)
            return f"Email sent to {email_to}"

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "Failed to send email to %s. Error: %s", email_to, e, exc_info=True
        )
        return None
