import pytest

from django.test import Client

from accounts.models import Customer
from accounts.views import (
    _get_credentials,
    check_mail_validity,
)


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


def _mock_get_credentials(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    return username, password


class MockRequest:
    def __init__(self, method):
        self.method = method.upper()

        if self.method == 'POST':
            self.POST = credentials


def test_get_credentials():

    request = MockRequest("POST")

    print("Should get credentials of user from a form with POST method")
    assert _get_credentials(request) == ('toto@email.fr', '12345678')


def test_check_email_validity(monkeypatch):

    def mock_validate_email(email):
        print("Dans le mock")
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
