import logging
from random import randint
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model, login, logout, authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from products.models import L_Favorite
from accounts.models import Customer
from accounts.constants import (
    OTP_VALIDITY_DURATION_IN_MINUTE,
    USER_LARA_CROFT,
)
from accounts.utils import (
    create_random_chars,
    send_email,
)


User = get_user_model()


# Get credentials sent via the form
def _get_credentials(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    return username, password


# Get OTP and password sent via the form
def _get_otp_n_pswd_from_request(request):
    otp_code = request.POST.get('otp', None)
    password = request.POST.get('password', None)
    return otp_code, password


# Check if the email is properly formed
def check_mail_validity(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def create_otp():
    """Create OTP (One Time Password) with a datetime validity"""

    # Create OTP_code
    otp_code = create_random_chars(randint(8, 12))

    # Create end datetime of otp_code
    now = datetime.now()
    otp_end_datetime = now + timedelta(minutes=OTP_VALIDITY_DURATION_IN_MINUTE)

    return otp_code, otp_end_datetime


def forgoten_pswd(request):
    list(messages.get_messages(request))  # Clear all system messages

    if request.method == 'POST':
        email, _ = _get_credentials(request)

        if not email:
            messages.success(request, ("Vous devez entrer votre adresse e-mail !"))
            return render(request, 'accounts/forgoten_pswd.html')

        if is_email_valid := check_mail_validity(email):

            otp_code, otp_validity_end_datetime = create_otp()

            customer = Customer.objects.get(username=email)
            if customer:
                customer.otp = otp_code
                customer.otp_validity_end_datetime = otp_validity_end_datetime
                customer.save()

                is_email_sent = send_email(email, otp_code, OTP_VALIDITY_DURATION_IN_MINUTE)
                if is_email_sent:
                    return redirect('accounts_new_pswd')

                messages.success(request, ("Une erreur inattendue est survenue !"))

    return render(request, "accounts/forgoten_pswd.html")


def login_user(request):
    list(messages.get_messages(request))  # Clear all system messages

    if request.method == 'POST':
        username, password = _get_credentials(request)

        if not username or not password:
            messages.success(request, ("Tous les champs doivent être remplis !"))
            return render(request, 'accounts/signup.html')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('products_home')

        messages.success(request, ("Identifiants incorrects !"))

    return render(request, "accounts/login.html")


def logout_user(request):
    logout(request)
    return redirect('products_home')


def new_pswd(request):
    list(messages.get_messages(request))  # Clear all system messages

    if request.method == 'POST':
        otp_code, password = _get_otp_n_pswd_from_request(request)

        if not otp_code or not password:
            messages.success(request, ("Tous les champs doivent être remplis !"))
            return render(request, 'accounts/new_pswd.html')

        try:
            # Get the user corresponding to the OTP and OTP validity end datetime
            user = Customer.objects.get(
                Q(otp=otp_code) & Q(otp_validity_end_datetime__gte=datetime.now()))

            # Update the user's password
            user.set_password(password)
            user.save()

            # Connect the user
            login(request, user)

            return redirect('products_home')

        except ObjectDoesNotExist:
            logging.debug("No customer found for this otp and valdity datetime")

        messages.success(request, ("Code OTP non valide !"))

    return render(request, "accounts/new_pswd.html")


def signup_user(request):
    list(messages.get_messages(request))  # Clear all system messages

    if request.method == 'POST':  # requête via formulaire
        username, password = _get_credentials(request)

        if not username or not password:
            messages.success(request, ("Tous les champs doivent être remplis !"))
            return render(request, 'accounts/signup.html')

        is_username_valid = check_mail_validity(username)  # because user email is used as username
        if not is_username_valid:
            messages.success(request, ("Email incorrect !"))
            return render(request, 'accounts/signup.html')

        try:
            # Creation of the user
            user = User.objects.create_user(
                username=username[:150], password=password, email=username[:150])

            # User connection
            login(request, user)

            return redirect('products_home')

        except Exception as e:
            print(str(e))
            if "exists" in str(e):
                messages.success(request, ("Cet utilisateur est déjà enregistré !"))

    return render(request, "accounts/signup.html")


def account(request):
    username = request.POST.get('username', '')
    first_name = request.POST.get('first_name', "")
    last_name = request.POST.get('last_name', "")
    is_submit_button_clicked = request.POST.get('is_submit_button_clicked', "")

    context = {"first_name": first_name, "last_name": last_name}

    try:
        if is_submit_button_clicked and username:
            (Customer.objects.filter(username=username)
                .update(first_name=first_name, last_name=last_name))

            messages.success(request, ("Votre compte a bien été mis à jour"))

    except Exception as e:
        logging.error(f"Unable to update account. Reason: {str(e)}")
        messages.success(request, (
            "Malheureusement une erreur du système est survenue. "
            "Les données n'ont pas pu être mises à jour. "
            "Merci de ré-essayez plus tard."))

    return render(request, "accounts/account.html", context=context)


def delete_fake_users(request):
    try:
        user = Customer.objects.get(username=USER_LARA_CROFT["username"])

        L_Favorite.objects.filter(customer_id=user.id).delete()
        Customer.objects.filter(username=USER_LARA_CROFT["username"]).delete()
    except Exception as e:
        print(str(e))

    return redirect('products_home')
