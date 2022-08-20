import pytest

from products.models import Category
from products.models import Product as SUT
from src.tests.products.params_for_mark_parametrize.products_objs import welformed_products


# Create a virtual database then destroy it after all tests have finished.
pytestmark = pytest.mark.django_db

categories_dict = {}  # keys will be names, values will be instances of Category


@pytest.fixture
def store_categories_in_db():
    # Create categories from the attribute 'categories' of each downloaded product
    # so that a product can be added to the database and get included in a stored category
    categories = set(
        category for product in welformed_products
        for category in product.categories)

    for category in categories:
        categories_dict[category] = Category.objects.create(name=category)

    return categories_dict


@pytest.fixture
def add_products_to_db(store_categories_in_db):
    SUT.add_many(welformed_products)


class TestProductModel:
    # @pytest.mark.test_me
    def test_add_many(self, caplog, store_categories_in_db):
        caplog.clear()

        # Store categories in the db
        # so that it is possible to add products and relies them to categories
        store_categories_in_db

        print("A list of elements that are not instances of WellFormedProduct should raise "
                " an exception and return False because the product can't be stored in "
                "the database.")
        assert SUT.add_many(
            ["not", "list", "of", "instance", "of", "WellFormedProduct"]) == False
        assert caplog.text != None
        caplog.clear()

        print("A list of welformed products should store all of the products then return True.")
        assert SUT.add_many(
            welformed_products) == True

        assert SUT.objects.all().count() == 5

    def test_find_original_products(self, add_products_to_db):

        print("Preparing the database for testing...")
        store_categories_in_db   # To create categories_dict

        print("Have the products been added to the database?: ", SUT.add_many(welformed_products))
        print("Database is now OK.")

        print(
            "'beverage' as keyword should return all products containing the keyword 'beverage'")

        original_products = SUT.find_original_products("beverage")
        assert len(original_products) == 5

        print(
            "'beverage orange' as keywords should return an empty Queryset because no product "
            "contains ALL these keywords (None of the products contains 'orange' AND 'beverage'"
            " in keywords)")

        original_products = SUT.find_original_products("beverage orange")
        assert list(original_products) == []

        print(
            "'beverage lemon light' as keywords should return only one product because only one "
            "product contains ALL these keywords")

        original_products = SUT.find_original_products("beverage lemon light")
        assert len(original_products) == 1
        assert original_products[0].name == "Lemonade light"

    def test_find_substitute_products(self, add_products_to_db):
        add_products_to_db

        print("An original product")
        cool_cola_with_score_e = SUT.objects.get(original_id=123457)

        substitutes = SUT.find_substitute_products(
            str(cool_cola_with_score_e.id),
            cool_cola_with_score_e.nutriscore_grade)

        print("     should return a lis of dicts where a product is a dict")
        assert isinstance(substitutes, list)
        assert isinstance(substitutes[0], dict)

        print("     should return a substitue product with a better nutriscore grade")
        assert substitutes[0]["nutriscore_grade"] < cool_cola_with_score_e.nutriscore_grade

        print("     should return a list of products ordered from the heavy wheight "
                "(number of categories in common) to the lighter")
        assert substitutes[0]["weight"] > substitutes[-1]["weight"]

        print("An original product that does not have a better substitute ")
        natural_carb_water_with_score_a = SUT.objects.get(original_id=123460)

        substitutes = SUT.find_substitute_products(
            str(natural_carb_water_with_score_a.id),
            natural_carb_water_with_score_a.nutriscore_grade)

        print("     should return an empty list")
        assert substitutes == []

        print("A non string original product ID should raise an exception")
        with pytest.raises(Exception):
            SUT.find_substitute_products(
                natural_carb_water_with_score_a.id,
                natural_carb_water_with_score_a.nutriscore_grade)

        print("An empty string as original product ID should raise an exception")
        with pytest.raises(Exception):
            SUT.find_substitute_products(
                "",
                natural_carb_water_with_score_a.nutriscore_grade)

        print("A non string original nutriscore_grade should raise an exception")
        with pytest.raises(Exception):
            SUT.find_substitute_products(
                str(natural_carb_water_with_score_a.id),
                ["a"])

        print("An empty string as original nutriscore_grade should raise an exception")
        with pytest.raises(Exception):
            SUT.find_substitute_products(
                str(natural_carb_water_with_score_a.id),
                "")
