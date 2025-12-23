"""src/worker.py."""

import logging
import smtplib
from email.message import EmailMessage
from celery import Celery
from src.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format=(
        "[%(asctime)s: %(levelname)s/%(processName)s] "
        "[%(task_name)s(%(task_id)s)] %(message)s"
    ),
)


@celery_app.task(name="send_email_task")
def send_email_task(email_to: str, subject: str, body: str):
    """
    Задача Celery для отправки email.
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
