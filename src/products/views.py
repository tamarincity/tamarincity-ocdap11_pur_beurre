import logging

from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from products.models import Product, ReceivedMessage, L_Favorite
from products import utils


User = get_user_model()


def home(request):
    return render(request, "products/home.html")


def add_to_favorites(request):
    is_submit_button_clicked = request.POST.get("is_submit_button_clicked", "")
    original_id = request.POST.get("original_id", "")
    substitute_id = request.POST.get("substitute_id", "")
    user_id = request.POST.get("user_id", "")

    if not user_id or user_id == "None" or not request.user.is_authenticated:
        messages.success(
            request, ("Vous devez être connecté pour accéder à cette fonctionnalité")
        )
        return redirect(request.META["HTTP_REFERER"])

    if is_submit_button_clicked and original_id and substitute_id and user_id:

        try:
            L_Favorite.objects.get_or_create(
                customer_id=user_id,
                original_product_id=original_id,
                substitute_product_id=substitute_id,
            )

            messages.success(
                request,
                ("Ce produit a bien été enregistré dans vos aliments préférés."),
            )
            return redirect(request.META.get("HTTP_REFERER"))

        except Exception as e:
            logging.error(f"Failed to create favorites! Reason: {str(e)}")
            messages.success(
                request,
                (
                    "Hélas, une erreur du système est survenue. "
                    "Merci de ré-essayer ultérieurement."
                ),
            )

    return redirect(request.META["HTTP_REFERER"])


def check_email(email):
    if email and isinstance(email, str) and email.count("@") == 1:

        right_part = email.split("@")[-1]

        if "." in right_part:
            return True

    return False


def contact(request):
    return render(request, "products/contact.html")


@login_required
def get_all_favorites(request):
    user_id = request.GET.get("user_id", "")

    favorites_rows = L_Favorite.objects.all().filter(customer_id=user_id)
    favorite_ids = set(row.substitute_product_id for row in favorites_rows)
    favorite_products = Product.objects.filter(id__in=favorite_ids)

    if len(favorite_products) == 0:
        messages.success(
            request,
            ("Il n'y a pas encore de produit enregistré dans vos aliments préférés."),
        )
        return render(request, "products/favorites.html")

    context = {"favorite_products": favorite_products}

    return render(request, "products/favorites.html", context)


def get_message(request):

    list(messages.get_messages(request))  # Clear all system messages

    firstname = request.POST.get("firstname", "")
    lastname = request.POST.get("lastname", "")
    email = request.POST.get("email", "")
    phone_number = request.POST.get("phone_number", "")
    message = request.POST.get("message", "")

    context = {
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "phone_number": phone_number,
        "message": message,
    }

    is_email_well_formed = check_email(email)
    if not is_email_well_formed:
        messages.success(request, ("Le champ email est incorrect !"))
        return render(request, "products/contact.html", context)

    if not (
        firstname
        and lastname
        and email
        and phone_number
        and message
        and isinstance(firstname, str)
        and isinstance(lastname, str)
        and isinstance(email, str)
        and isinstance(phone_number, str)
        and isinstance(message, str)
    ):

        messages.success(request, ("Tous les champs doivent être remplis !"))
        return render(request, "products/contact.html", context)

    try:
        ReceivedMessage.objects.create(
            firstname=firstname,
            lastname=lastname,
            email=email,
            phone_number=phone_number,
            message=message,
        )

        messages.success(
            request,
            (
                "Votre message a bien été reçu. Il sera traité dans les plus brefs délais."
            ),
        )
    except Exception as e:
        logging.error(f"Unable to add the customer. Reason: {str(e)}")
        messages.success(
            request,
            (
                "Malheureusement, une erreur du système est survenue. "
                "Le message n'a pas pu être reçu !"
                " Veuillez ré-essayer plus tard. Merci"
            ),
        )

    return render(request, "products/message_received.html")


def get_origial_product(request):
    """Beforehand, the user has entered keywords to find the original product he
    wants to replace.
    Through this route, we try to find the original product.
    If only one product is found, the user is redirected to the list of matching
    substitute products.
    Otherwise, we return a list of original products that match the keywords. This
    way, the user can choose the right original product.
    """

    try:
        keywords = request.GET["keywords_of_original_product"]
    except Exception as e:
        logging.error("No keywords found for original product")
        logging.error(str(e))
        return render(request, "products/originals.html")

    original_products: list[Product] = None
    if keywords and isinstance(keywords, str):

        keywords = utils.format_text(keywords)
        original_products = Product.find_original_products(keywords)

    if len(original_products) == 0:
        logging.info("No original products found!")
        messages.success(
            request, ("Aucun produit trouvé ! Essayez avec d'autres mots-clefs.")
        )

    # If there is only one original product found then should redirect to get substitutes
    if original_products and len(original_products) == 1:
        logging.info("Redirect to get_substitutes")
        return redirect(
            reverse("products_get_substitutes") + f"?id={original_products[0].id}"
            f"&nutriscore_grade={original_products[0].nutriscore_grade}"
        )

    # Many products found should return the list so the user can choose the good one
    logging.info("Render a list of products found as original products")
    return render(
        request, "products/originals.html", {"original_products": original_products}
    )


def get_substitutes(request):
    """This route returns a list of substitute products corresponding to the given
    original product ID.
    """

    original_product_id = request.GET.get("id")
    nutriscore_grade = request.GET.get("nutriscore_grade")

    substitute_products = Product.find_substitute_products(
        original_product_id, nutriscore_grade
    )

    if len(substitute_products) == 0:
        logging.info("No original products found!")
        messages.success(
            request, ("Il n'y a pas de meilleurs produit qui soit similaire")
        )

    original_product = Product.objects.get(id=original_product_id)

    return render(
        request,
        "products/substitutes.html",
        {
            "substitute_products": substitute_products,
            "original_product": original_product,
        },
    )


def legal_notice(request):
    return render(request, "products/legal_notice.html")


def details(request):

    if original_product := request.GET.get("original_id", ""):
        original_product = Product.objects.get(id=request.GET.get("original_id"))

    if substitute_product := request.GET.get("substitute_id", ""):
        substitute_product = Product.objects.get(id=request.GET.get("substitute_id"))

    return render(
        request,
        "products/details.html",
        context={
            "original_product": original_product,
            "substitute_product": substitute_product,
        },
    )
