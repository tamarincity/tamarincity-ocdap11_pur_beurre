from datetime import datetime

import pytest

from django.test import Client

from accounts.models import Customer
from accounts.utils import (
    create_random_chars,
    send_email,
)

from icecream import ic


client = Client()


def test_create_random_chars():

    print("Should return a random string")
    assert type(create_random_chars(7)) == str

    print("The returned length (7) must be equal to the integer entered as argument (7)")
    assert len(create_random_chars(7)) == 7

    print("Two returned strings of the same length must have a different content")
    assert create_random_chars(5) != create_random_chars(5)


def test_send_email(monkeypatch):

    now = datetime.now()

    def mock_send_mail(
            subject,
            message,
            email_host_user,
            recipients,
            fail_silently):

        for recipient in recipients:
            if not (
                    "@" in recipient
                    and "." in recipient):
                raise Exception("Sending email failed")
        return True

    monkeypatch.setattr("accounts.utils.send_mail", mock_send_mail)

    print("If the email of the recipient is malformed "
            "then should return False because no email can be sent")
    assert send_email("wrong@email", "this_is_the_OTP_code", now) == False

    print("If the email of the recipient is properly formed "
            "then should return True because the email has been sent")
    assert send_email("good@email.com", "this_is_the_OTP_code", now) == True
