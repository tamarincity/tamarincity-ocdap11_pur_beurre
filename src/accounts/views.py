import logging

from django.contrib.auth import get_user_model, login, logout, authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render, redirect

from products.models import L_Favorite
from accounts.models import Customer
from accounts.constants import USER_LARA_CROFT


User = get_user_model()


# Get credentials sent via the form
def _get_credentials(request):
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    return username, password


# Check if the email is properly formed
def check_mail_validity(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


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
