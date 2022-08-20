import logging

from django.test import Client
from django.urls import reverse

import pytest

from products.models import Category, Customer, L_Favorite, Product
from src.tests.products.params_for_mark_parametrize.products_objs import welformed_products
import src.products.views as sut


client = Client()

# Create a virtual database then destroy it after all tests have finished.
pytestmark = pytest.mark.django_db

substitutes_list1 = [
    {
        "id": 12312311,
        "nutriscore_grade": "b",
        "name": "substitute product name 1",
        "weight": 4},
    {
        "id": 12312312,
        "nutriscore_grade": "b",
        "name": "substitute product name 2",
        "weight": 3},
    {
        "id": 12312313,
        "nutriscore_grade": "a",
        "name": "substitute product name 3",
        "weight": 2}]

substitutes_list2 = [
    {
        "id": 12312311,
        "nutriscore_grade": "a  ",
        "name": "substitute product name 1",
        "weight": 4},
    {
        "id": 12312312,
        "nutriscore_grade": "a",
        "name": "substitute product name 2",
        "weight": 3},
    {
        "id": 12312313,
        "nutriscore_grade": "a",
        "name": "substitute product name 3",
        "weight": 2}]

userid_n_productids = {
    "is_submit_button_clicked": "yes",
    "original_id": "1",
    "substitute_id": "2",
    "user_id": "1"}

favoriteids_without_user_info = {
    "is_submit_button_clicked": "yes",
    "original_id": "1",
    "substitute_id": "2"}


def add_a_category():
    return Category.objects.create(name="Category name")


def add_a_product():
    return Product.objects.create(
        name="Product name",
        brands="brand1, brand2",
        code=8714100614754,
        original_id=9876543210,
        quantity="Quantity 1.5l",
        image_thumb_url="url-thumb-image",
        image_url="url-thumb-image",
        ingredients_text="list of ingredients",
        keywords="some keywords (mega key_words)",
        nutriments="Some nutriments",
        nutriscore_grade="c",
        stores="All the stores where you can find the product",
        url="url_of_the_website_of_the_product",
    )


categories_dict = {}  # keys will be names, values will be instances of Category


@pytest.fixture
def store_categories_in_db():
    # Create categories from the attribute 'categories' of each downloaded product
    # so that a product can be added to the database and get included in a stored category
    categories = set(
        category
        for product in welformed_products
            for category in product.categories)

    for category in categories:
        categories_dict[category] = Category.objects.create(name=category)

    return categories_dict


@pytest.fixture
def add_products_to_db(store_categories_in_db):
    store_categories_in_db
    Product.add_many(welformed_products)


@pytest.fixture
def add_customer_to_db():
    return Customer.objects.create_user(
                username="tomb@raider.fr", password="12345678", email="tomb@raider.fr")


@pytest.fixture
def get_user_credentials():
    return {"username": "tomb@raider.fr", "password": "12345678", "email": "tomb@raider.fr"}


@pytest.mark.integration_test
def test_home():

    print("No end-point after the domain name should take the user to the home page")
    response = client.get('')
    assert response.templates[0].name == 'products/home.html'


@pytest.mark.integration_test
def test_contact():

    print("'products_contact' as URL should take the user to the contact page")
    response = client.get('/products_contact')
    assert response.templates[0].name == 'products/contact.html'


def test_check_email():
    print("Malformed email address should return False")
    assert sut.check_email("malformed@email") == False

    print("Properly formed email address should return True")
    assert sut.check_email("malformed@email.com") == True


@pytest.mark.integration_test
def test_get_substitutes(monkeypatch, caplog):
    caplog.clear()

    def mock_find_substitute_products(id, nutriscore_grade):
        try:
            if not (id
                    and isinstance(id, str)):
                raise Exception("id must be string and not empty")
            if not (nutriscore_grade
                    and isinstance(nutriscore_grade, str)):
                raise Exception("nutriscore_grade must be string and not empty")
            int(id)
        except Exception as e:
            print(f"Exception raised: {str(e)}")

        if nutriscore_grade > "b":
            return substitutes_list1

        if nutriscore_grade == "b":
            return substitutes_list2

        return []

    monkeypatch.setattr(Product, "find_substitute_products", mock_find_substitute_products)

    print("An original product id that doesn't exist should raise an exception")
    with pytest.raises(Exception):
        response = client.get('/get-substitutes', {'id': '9995288', 'nutriscore_grade': "c"})

    print("An original product")
    add_a_category()
    add_a_product()
    response = client.get('/get-substitutes', {'id': '1', 'nutriscore_grade': "c"})

    print("     should return a context that contains a list of products")
    print("         with a better  nutriscore_grade")
    assert all(
        product["nutriscore_grade"] < "c" for product in response.context["substitute_products"])

    print("         orded by weight (from the heaviest to the lightest)")

    substitute_products = response.context["substitute_products"]
    assert (substitute_products[0]["weight"] > substitute_products[-1]["weight"])

    print("     should return a context that contains the original product")
    assert response.context["original_product"] == Product.objects.get(id=1)

    print("An original product that doesn't have a better substitute "
            "should return 'Il n'y a pas de meilleurs produit qui soit similaire' "
            "as a message")
    response = client.get('/get-substitutes', {'id': '1', 'nutriscore_grade': "a"})
    assert "Il n&#x27;y a pas de meilleurs produit qui soit similaire" in str(response.content)


@pytest.mark.integration_test
def test_add_to_favorites(
        add_customer_to_db, add_products_to_db, caplog):

    caplog.set_level(logging.INFO)

    user = add_customer_to_db
    add_products_to_db

    caplog.clear()
    print("Trying to add favorites")
    with pytest.raises(KeyError):  # equiv to assert for exceptions
        client.post('/add_to_favorites', favoriteids_without_user_info)

    print("     should redirect to previous page even though it didn't succeed")
    assert "HTTP_REFERER" in caplog.text

    print("A unauthenticated customer should not be able to store his favorite products")
    assert L_Favorite.objects.all().count() == 0

    caplog.clear()
    print("If user is connected then "
            "Providing customer ID, Original product ID and Substitute product ID ")
    client.force_login(user)
    with pytest.raises(KeyError):  # equiv to assert for exceptions
        client.post('/add_to_favorites', userid_n_productids)

    print("     should add favorites to the database")
    favorite = L_Favorite.objects.get(customer_id=userid_n_productids["user_id"])
    assert (favorite.original_product_id == int(userid_n_productids["original_id"])
            and favorite.substitute_product_id == int(userid_n_productids["substitute_id"]))
    caplog.clear()
    client.logout()


@pytest.mark.integration_test
def test_get_all_favorites(add_customer_to_db, add_products_to_db):

    user = add_customer_to_db
    add_products_to_db

    client.force_login(user)

    print("A logged user should get taken to the favorites page.")
    response = client.get('/products_favorites', {"user_id": user.id})
    assert response.templates[0].name == 'products/favorites.html'

    print("A logged user who has no favorites should return the message: "
            "'Il n'y a pas encore de produit enregistré dans vos aliments préférés.'")
    assert ("Il n&#x27;y a pas encore de produit enregistr" in str(response.content))
    assert ("dans vos aliments pr" in str(response.content))

    print("A user who has already add 2 products to his favorites ")
    print("       should be able to see them in the favorites page")
    # Add favorite products
    L_Favorite.objects.get_or_create(
                customer_id=user.id,
                original_product_id=2,
                substitute_product_id=3)  # Lemonade light

    L_Favorite.objects.get_or_create(
                customer_id=user.id,
                original_product_id=1,
                substitute_product_id=5)  # Natural carbonated water

    response = client.get('/products_favorites', {"user_id": user.id})
    assert "Lemonade light" in str(response.content)
    assert "Natural carbonated water" in str(response.content)

    print("       should see only 2 products and not less.")
    assert len(response.context["favorite_products"]) == 2
    client.logout()

    print("A unauthenticated user should not return a file.")
    response = client.get('/products_favorites', {"user_id": user.id})
    assert len(response.templates) == 0


@pytest.mark.integration_test
def test_get_origial_product(caplog, add_products_to_db):
    caplog.set_level(logging.INFO)
    caplog.clear()
    add_products_to_db

    url = "/products_get-origial-product"

    print("No keyword provided")
    print("     should log an error: 'No keywords found for original product'")

    response = client.get(url)
    assert "ERROR" in caplog.text
    assert "No keywords found for original product" in caplog.text

    print("     should serve the file 'products/originals.html'")
    assert response.templates[0].name == 'products/originals.html'

    print("If many products contain the keywords then")
    print("     should return the concerned products")
    context = {"keywords_of_original_product": "Lemonade"}

    response = client.get(url, context)
    assert len(response.context["original_products"]) == 2
    assert all(
        "lemonade" in product.keywords for product in response.context["original_products"])

    print("     should log as info: 'Render a list of products found as original products'.")
    assert "Render a list of products found as original products" in caplog.text
    caplog.clear()

    print("If only ONE product contains ALL the keywords then")
    print("     should redirect to the substitutes page with original product_id and "
            "nutriscore_grade as query")

    context = {"keywords_of_original_product": "Lemonade light"}
    response = client.get(url, context)
    assert response['Location'] == (reverse('products_get_substitutes')
                                    + '?id=3'
                                    '&nutriscore_grade=b')

    print("     Should log an info: 'Redirect to get_substitutes'")
    assert "Redirect to get_substitutes" in caplog.text
    caplog.clear()

    print("If no products contain absolutly ALL the keywords then ")
    print("     should log an info: 'No original products found!'")
    context = {"keywords_of_original_product": "Lemonade light chocolate"}
    response = client.get(url, context, follow=True)
    assert "No original products found!" in caplog.text

    print("     should display on the page the alert: 'Aucun produit "
            "trouvé ! Essayez avec d'autres mots-clefs.'")
    context = {"keywords_of_original_product": "Lemonade light ultra"}
    assert "alert" in str(response.content)
    assert "Aucun produit trouv" in str(response.content)
    assert "Essayez avec d" in str(response.content)
    assert "autres mots-clefs." in str(response.content)


@pytest.mark.integration_test
def test_legal_notice():
    print("This view should return the page 'products/legal_notice.html'")
    response = client.get('/products_legal_notice')
    assert response.templates[0].name == 'products/legal_notice.html'


@pytest.mark.integration_test
def test_details(caplog, add_products_to_db):
    caplog.set_level(logging.INFO)
    caplog.clear()
    add_products_to_db

    print("Original product ID and Substitute product ID as argument")
    print("     should render the details page")
    response = client.get('/products_details', {"original_id": 1, "substitute_id": 3})
    assert response.templates[0].name == 'products/details.html'

    print("     should send to the page: the original product and the substitute one")
    assert response.context["original_product"].name == "Lemonade"
    assert response.context["substitute_product"].name == "Lemonade light"


@pytest.mark.integration_test
def test_get_message():

    print("No data sent to the page should serve the page of contact")
    response = client.post('/products_get-message')
    assert response.templates[0].name == "products/contact.html"

    print("Any missing required data should serve the page of contact with the folowing "
            "message: 'Tous les champs doivent être remplis !'")
    context = {
                "firstname": "Mickey",
                "lastname": "Mouse",
                "email": "mickey@mouse.us",
                "phone_number": "",
                "message": "Hello !"}

    response = client.post('/products_get-message', context)
    assert response.templates[0].name == "products/contact.html"
    assert "alert" in str(response.content)
    assert "Tous les champs doivent " in str(response.content)
    assert "tre remplis " in str(response.content)

    print("If the email address is not properly formed then should serve the page "
            "of contact with the folowing message: 'Le champ email est incorrect !'")
    context = {
                "firstname": "Mickey",
                "lastname": "Mouse",
                "email": "mickey@mouse",
                "phone_number": "1234567890",
                "message": "Hello !"}

    response = client.post('/products_get-message', context)
    assert response.templates[0].name == "products/contact.html"
    assert "alert" in str(response.content)
    assert "Le champ email est incorrect " in str(response.content)

    print("If all the required fields are present then")
    print("     should serve the page of received message")
    context = {
                "firstname": "Mickey",
                "lastname": "Mouse",
                "email": "mickey@mouse.us",
                "phone_number": "1234567890",
                "message": "Hello !"}

    response = client.post('/products_get-message', context)
    assert response.templates[0].name == "products/message_received.html"

    print("     should display the folowing message: "
            "'Votre message a bien été reçu. Il sera traité dans les plus brefs délais.'")
    assert "alert" in str(response.content)
    assert "Votre message a bien " in str(response.content)
    assert "Il sera trait" in str(response.content)
    assert " dans les plus brefs d" in str(response.content)


@pytest.mark.integration_test
def test_delete_fake_users():
    response = client.get('/accounts_delete_fake_users', follow=True)
    assert response.templates[0].name == 'products/home.html'
