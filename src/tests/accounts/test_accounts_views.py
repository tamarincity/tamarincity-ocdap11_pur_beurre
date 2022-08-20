from datetime import datetime, timedelta
from functools import total_ordering

import pytest

from django.test import Client


from accounts.models import Customer
from accounts.views import (
    _get_credentials,
    _get_otp_n_pswd_from_request,
    check_mail_validity,
    create_otp,
)
from accounts.constants import OTP_VALIDITY_DURATION_IN_MINUTE


client = Client()

# Create a virtual database then destroy it after all tests have finished.
pytestmark = pytest.mark.django_db

credentials = {
                "username": "toto@email.fr",
                "first_name": "Toto",
                "last_name": "Toto",
                "email": "toto@email.fr",
                "password": "12345678",
                "is_submit_button_clicked": "yes"}

otp_n_pswd = {"otp": "Je 5u1s l3 c0de 0TP", "password": "new_password"}


def _mock_get_credentials(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    return username, password


class MockRequest:
    def __init__(self, method):
        self.method = method.upper()

        if self.method == 'POST_CREDENTIALS':
            self.POST = credentials
        if self.method == 'POST_OTP_N_PSWD':
            self.POST = otp_n_pswd


def test_get_credentials():

    request = MockRequest("POST_CREDENTIALS")

    print("Should get credentials of user from a form with POST method")
    assert _get_credentials(request) == ('toto@email.fr', '12345678')


def test_get_otp_n_pswd_from_request():

    request = MockRequest("POST_OTP_N_PSWD")

    print("Should get OTP and password sent by the user via a form with POST method")
    assert _get_otp_n_pswd_from_request(request) == ("Je 5u1s l3 c0de 0TP", "new_password")


def test_check_email_validity(monkeypatch):

    def mock_validate_email(email):
        if "@" in email:
            right_part = email.split('@')[1]
            if "." in right_part:
                return True

        raise Exception('Invalid email address')

    monkeypatch.setattr("src.accounts.views.validate_email", mock_validate_email)

    print("Should return True if if the email address is valid")
    assert check_mail_validity("toto@dupont.fr") == True

    print("Should return False if if the email address is NOT valid")
    assert check_mail_validity("toto@dupont") == False


@pytest.mark.integration_test
def test_login_user(monkeypatch):

    def mock_authenticate(username, password):
        if (username == credentials["username"]
                and password == credentials["password"]):
            return True
        return False

    def mock_login(request, user):
        pass

    monkeypatch.setattr("accounts.views.authenticate", mock_authenticate)
    monkeypatch.setattr("accounts.views.login", mock_login)

    print("If no username or no password is provided in login then should return "
            "'Tous les champs doivent être remplis' as message")
    response = client.post('/accounts_login', {"no_usernam": "", "no_password": ""})
    assert ("alert" in str(response.content)
            and "Tous les champs doivent" in str(response.content)
            and "remplis" in str(response.content))

    print("If username is not registered or password is incorrect then should return "
            "'Identifiants incorrects' as message")
    response = client.post(
        '/accounts_login', {"username": credentials["username"], "password": "XXX"})
    assert ("alert" in str(response.content)
            and "Identifiants incorrects" in str(response.content))

    print("If username and password are correct then should redirect to the home page")
    # follow=True allows to follow redirection
    response = client.post(
        '/accounts_login', {"username": credentials["username"],
                            "password": credentials["password"]}, follow=True)

    assert (response.redirect_chain[0][0] == "/")  # redirect_chain = [('/', 302)]


@pytest.mark.integration_test
def test_logout_user(monkeypatch):

    def mock_logout(request):
        pass

    monkeypatch.setattr("accounts.views.logout", mock_logout)

    print("If logout is clicked then ")
    print("     should redirect to the home page")
    # follow=True allows to follow redirection
    response = client.get('/accounts_logout', follow=True)
    assert (response.redirect_chain[0][0] == "/")  # redirect_chain = [('/', 302)]

    print("     should display the link 'Connexion'")
    assert "Connexion" in str(response.content)


@pytest.mark.integration_test
def test_signup_user(monkeypatch):

    def mock_get_credentials(request):
        return _mock_get_credentials(request)

    def mock_check_mail_validity(email: str) -> bool:
        if (email
                and isinstance(email, str)
                and email.count("@") == 1):

            right_part = email.split("@")[-1]

            if "." in right_part:
                return True
        return False

    def mock_login(request, user):
        if request.POST.get('username', None) == credentials["username"]:
            raise Exception("User already exists!")
        return True

    monkeypatch.setattr("accounts.views._get_credentials", mock_get_credentials)
    monkeypatch.setattr("accounts.views.check_mail_validity", mock_check_mail_validity)
    monkeypatch.setattr("accounts.views.login", mock_login)

    print("If username (email) or password is missing then "
            "should alert 'Tous les champs doivent être remplis !'")
    response = client.post(
        '/accounts_signup', {"username": credentials["username"], "password": ""})

    assert ("alert" in str(response.content)
            and "Tous les champs doivent" in str(response.content)
            and "remplis" in str(response.content))

    print("If username (email) is malformed then "
            "should alert 'Email incorrect !'")
    response = client.post(
        '/accounts_signup',
        {"username": "toto@email", "password": credentials["password"]})

    assert ("alert" in str(response.content)
            and "Email incorrect" in str(response.content))

    print("If user is already registered then "
            "should alert 'Cet utilisateur est déjà enregistré !'")
    response = client.post(
        '/accounts_signup',
        {"username": credentials["username"], "password": credentials["password"]})

    assert ("alert" in str(response.content)
            and "Cet utilisateur est d" in str(response.content)
            and "enregistr" in str(response.content))

    print("If user is not already registered then "
            "should redirect to the home page")
    response = client.post(
        '/accounts_signup',
        {"username": "new@user.fr", "password": credentials["password"]}, follow=True)

    assert (response.redirect_chain[0][0] == "/")  # redirect_chain = [('/', 302)]


@pytest.mark.integration_test
def test_account(monkeypatch):

    # Create a registered user
    Customer.objects.create(
        username=credentials["username"],
        first_name="",
        last_name="")

    print("If the registered user modify his account via the form then")
    print("     should alert 'Votre compte a bien été mis à jour'")
    response = client.post('/accounts_account', credentials)
    assert ("alert" in str(response.content)
                and "Votre compte a bien " in str(response.content)
                and "mis " in str(response.content)
                and "jour" in str(response.content))

    print("     should update the user account in the database")
    customer = Customer.objects.get(username=credentials["username"])
    assert customer.first_name == credentials["first_name"]
    assert customer.last_name == credentials["last_name"]


def test_create_otp(monkeypatch):

    def mock_create_random_chars(int):
        return "gTdo3ik326GTsc1d24h0jfRRYJBKGN020gTdo3ik326GTsc1d24h0jfRRYJBKGN020"[:int]

    monkeypatch.setattr("accounts.views.create_random_chars", mock_create_random_chars)

    otp_n_validity = create_otp()

    print("Should return a tuple of two elements")
    assert len(otp_n_validity) == 2

    print("The first returned element (OTP) should be a string")
    assert type(otp_n_validity[0]) == str

    print("The first returned element (OTP) should have a length from 8 to 12 included")
    assert 8 <= len(otp_n_validity[0]) <= 12

    print("The second returned element (otp_end_datetime) should be a datetime")
    assert type(otp_n_validity[1]) == datetime


@pytest.mark.integration_test
def test_forgoten_pswd(monkeypatch):

    now = datetime.now()
    otp_end_datetime = now + timedelta(minutes=OTP_VALIDITY_DURATION_IN_MINUTE)

    def mock_get_credentials(request):
        return _mock_get_credentials(request)

    def mock_check_mail_validity(email: str) -> bool:
        if (email
                and isinstance(email, str)
                and email.count("@") == 1):

            right_part = email.split("@")[-1]

            if "." in right_part:
                return True
        return False

    def mock_create_otp():
        return "I_4m_the_0TP", otp_end_datetime

    def mock_send_email(email, otp_code, OTP_VALIDITY_DURATION_IN_MINUTE):
        if "must_fail" in email:
            return False
        return True

    class MockCustomer():
        class objects():

            def get(username):
                class Toto():
                    def __init__(self, email):
                        self.username = email
                        self.password = credentials["password"]
                        self.otp = "Th3_old_0TP"
                        self.otp_validity_end_datetime = None

                    def save(self):
                        return
                if (username == credentials["username"]
                        or "must_fail" in username):
                    return Toto(username)

    monkeypatch.setattr("accounts.views._get_credentials", mock_get_credentials)
    monkeypatch.setattr("accounts.views.check_mail_validity", mock_check_mail_validity)
    monkeypatch.setattr("accounts.views.create_otp", mock_create_otp)
    monkeypatch.setattr("accounts.views.send_email", mock_send_email)
    monkeypatch.setattr("accounts.views.Customer", MockCustomer)

    print("No email provided should alert 'Vous devez entrer votre adresse e-mail !'")
    response = client.post(
        '/accounts_forgoten_pswd', {})
    assert "Vous devez entrer votre adresse e-mail" in str(response.content)

    print("If the email is malformed should display the page 'forgotten password' again")
    response = client.post(
        '/accounts_forgoten_pswd', {"username": "malformed@email"})
    assert "Mot de passe oubli" in str(response.content)

    print("If the email is not registered then "
            "should display the page 'forgotten password' again")
    response = client.post(
        '/accounts_forgoten_pswd', {"username": "malformed@email"})
    assert "Mot de passe oubli" in str(response.content)

    print("If the email is already registered but something went wrong "
            "while sending the email then")
    print("     should alert 'Une erreur inattendue est survenue'")
    response = client.post(
        '/accounts_forgoten_pswd', {"username": "sending.email@must_fail.com"})
    assert "Une erreur inattendue est survenue " in str(response.content)

    print("     should display the same form again")
    assert "Mot de passe oubli" in str(response.content)

    print("If the email is already registered and if an email has been sent "
            "then should redirect to the 'Enter your new password' page")
    response = client.post(
        '/accounts_forgoten_pswd',
        {"username": credentials["username"]},
        follow=True)  # To follow the redirection
    assert (response.redirect_chain[0][0] == "/accounts_new_pswd")  # Because follow=True


@pytest.mark.test_me
@pytest.mark.integration_test
def test_new_pswd(monkeypatch):

    now = datetime.now()
    otp_end_datetime = now + timedelta(minutes=OTP_VALIDITY_DURATION_IN_MINUTE)

    # Creation of a registered user so that we should be able to change his password
    registered_user, created = Customer.objects.get_or_create(
        username='calamity@jane.com',
        email='calamity@jane.com',
        password="old_p4SSw0rD",
        otp="R1ght_0TP",
        otp_validity_end_datetime=otp_end_datetime)

    def mock_get_otp_n_pswd_from_request(request):
        return request.POST.get('otp', None), request.POST.get('password', None)

    monkeypatch.setattr(
        "accounts.views._get_otp_n_pswd_from_request", mock_get_otp_n_pswd_from_request)

    print("If no OTP is provided from the form then should display the "
            "message: 'Tous les champs doivent être remplis'")
    response = client.post("/accounts_new_pswd", {"password": "new_PA55W0rd"})
    assert 'Tous les champs doivent ' in str(response.content)
    assert 'tre remplis' in str(response.content)

    print("If no password is provided from the form then should display the "
            "message: 'Tous les champs doivent être remplis'")
    response = client.post("/accounts_new_pswd", {"otp": "R1ght_0TP"})
    assert 'Tous les champs doivent ' in str(response.content)
    assert 'tre remplis' in str(response.content)

    print("If a wrong OTP is provided from the form then should display the "
            "message: 'Code OTP non valide'")
    response = client.post(
        "/accounts_new_pswd", {"otp": "Wr0ng_0TP", "password": "N3w_passw0rd"})
    assert 'Code OTP non valide ' in str(response.content)

    print("If the right OTP is provided from the form then")
    print("     should redirect to the home page")
    response = client.post(
        "/accounts_new_pswd",
        {"otp": "R1ght_0TP", "password": "N3w_passw0rd"},
        follow=True)  # To follow the redirection
    assert (response.redirect_chain[0][0] == "/")  # Because follow=True

    print("     should display the link to logout because "
            "the user is automatically logged in")
    assert "logout" in str(response.content)
