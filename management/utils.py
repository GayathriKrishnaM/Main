from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_notification_email(email, message):
    try:
        send_mail(
            'Order Confirmation - Thank You for Shopping with Ganga Restaurant!',
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send email to {email}. Error: {str(e)}")
