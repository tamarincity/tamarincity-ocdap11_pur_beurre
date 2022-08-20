import logging
from random import choice

from django.core.mail import send_mail
from django.conf import settings

from icecream import ic

from accounts.constants import (
    ALPHABET_N_NUMBERS,
)


def create_random_chars(nbr_of_chars):
    return (
        "".join(choice(ALPHABET_N_NUMBERS) for i in range(nbr_of_chars)))


def send_email(email, otp_code, otp_validity_duration_in_minute):
    """Send OTP and its validity duration via email"""

    recipient = email
    message = (
        f"Bonjour, vous avez 10 minutes "
            f"pour modifier votre mot de passe. Votre code OTP est: {otp_code}")

    subject = "Pur Beurre: Votre code OTP"

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient],
            fail_silently=False)

    except Exception as e:
        logging.error(f"ERROR, unable to send email! Reason: {e}")
        return False

    return True
