import pytest
import copy

from products import utils
from products import etl_transform as SUT
from products.etl_extract import WellFormedProduct
from tests.products.params_for_mark_parametrize.params_etl_extract import (
    good_downloaded_product,
)

from products.constants import (
    PRODUCT_NAME_MAX_LENGTH,
    QUANTITY_MAX_LENGTH,
    UNWANTED_CATEGORIES,
)

good_downloaded_product_as_object = WellFormedProduct(good_downloaded_product)
mega_keywords = (
    " name of the product pack 8 pieces 2kg farine et 33cl soda the "
    "brand the generic name of the product category_1, category_2 these are "
    "keywords 5012345678912 ")

product_with_mega_keyword_updated = copy.deepcopy(good_downloaded_product_as_object)
product_with_mega_keyword_updated.mega_keywords = mega_keywords


def test_str_to_list(caplog):

    str_to_turn_into_list = "category1,caTegory2,    category3, CATEGORY4"
    expected = ['Category1', 'Category2', 'Category3', 'Category4']

    print("None as string to turn into list: ")
    print("     should return None")
    assert SUT.str_to_list(None) == None
    print("     should log a warning")
    assert "WARNING" in caplog.text

    print("Non string as string to turn into list: ")
    print("     should return None")
    assert SUT.str_to_list(["not", "a", "string"]) == None
    print("     should log a warning")
    assert "WARNING" in caplog.text

    print(
        """Words separated by space should return all the words as one element of """
        """a list.
        All the words should be lower case except for the first one
        that should be capitalized""")
    assert SUT.str_to_list("word1 word2   WORD3") == ["Word1 word2   word3"]

    print("Words separated by coma should return a list of capitalized words.")
    assert SUT.str_to_list(str_to_turn_into_list) == expected


def test_remove_products_with_unwanted_categories():

    print("No categories should return None so the product should be removed")
    assert SUT.remove_products_with_unwanted_categories("") == None

    print("Non list as categories should raise TypeError")
    with pytest.raises(TypeError):
        SUT.remove_products_with_unwanted_categories("cat1, cat2, cat3")

    print("Any of an unwanted category in a list of categories "
            "should return None so the product should be removed")
    for unwanted_category in UNWANTED_CATEGORIES:
        assert SUT.remove_products_with_unwanted_categories(
            [unwanted_category, "good category"]) == None

    print("A list of categories with some empty categories "
            "should return the list without the empty categories")
    assert SUT.remove_products_with_unwanted_categories(
        ["cat1", "", "cat2", None]) == ['cat1', 'cat2']


def test_add_mega_keywords_to_product(monkeypatch):

    def mock_format_text(text_format):
        if text_format == (
                "Name Of The Product Pack de 8 pieces de 2 Kg de farine & "
                "330ml de SODA The Brand marque the generic name of the product category_1, "
                "category_2 these are keywords 5012345678912"):

            return mega_keywords
        return ""

    monkeypatch.setattr(utils, "format_text", mock_format_text)

    print("Any product which is not an instance of WellFormedProduct "
            "should return an exception")
    #  << good_downloaded_product >> is a dict instead of an instance of WellFormedProduct
    with pytest.raises(Exception):
        SUT.add_mega_keywords_to_product(good_downloaded_product)

    print("An instance of WellFormedProduct should return updated with an expected new "
            "value for the mega_keywords field")
    assert good_downloaded_product_as_object.mega_keywords == "True"
    assert product_with_mega_keyword_updated.mega_keywords == mega_keywords
    assert SUT.add_mega_keywords_to_product(
        good_downloaded_product_as_object) == product_with_mega_keyword_updated


def test_transform_product(monkeypatch):

    def mock_remove_products_with_unwanted_categories(list_of_categories):
        for unwanted in UNWANTED_CATEGORIES:
            if unwanted in list_of_categories:
                return None
        return list_of_categories

    def mock_add_mega_keywords_to_product(product_as_arg: WellFormedProduct):

        if not(product_as_arg
                and isinstance(product_as_arg, WellFormedProduct)):
            raise Exception("Error in products.etl_transform add_mega_keywords_to_product()"
                            ": product must be an instance of WellFormedProduct")

        product_as_arg.mega_keywords = (
            " "
            + "a" * (PRODUCT_NAME_MAX_LENGTH + 1)
            + mega_keywords[20:])
        return product_as_arg

    monkeypatch.setattr(
        SUT,
        "remove_products_with_unwanted_categories",
        mock_remove_products_with_unwanted_categories)

    monkeypatch.setattr(
        SUT,
        "add_mega_keywords_to_product",
        mock_add_mega_keywords_to_product)

    product_with_too_long_name = copy.deepcopy(good_downloaded_product_as_object)
    new_product_name = "a" * (PRODUCT_NAME_MAX_LENGTH + 1)
    product_with_too_long_name.product_name_fr = new_product_name

    transformed_product = SUT.transform_product(product_with_too_long_name)

    print("The downloaded product should have its categories attribute updated "
            "with expected values (empty categories removed)")
    assert transformed_product.categories == ['Category_1', 'Category_2']

    print("The downloaded product should have its quantity attribute updated "
            f"with an expected value with a length of {QUANTITY_MAX_LENGTH} max")
    assert transformed_product.quantity == "Pack de 8 pieces de 2 Kg de..."
    assert len(transformed_product.quantity) <= QUANTITY_MAX_LENGTH

    print("The downloaded product should have its product_name_fr attribute updated "
            f"with an expected value with a length of {PRODUCT_NAME_MAX_LENGTH} max")
    # assert transformed_product.product_name_fr == PRODUCT_NAME_MAX_LENGTH
    assert len(transformed_product.product_name_fr) <= PRODUCT_NAME_MAX_LENGTH

    print("The downloaded product should have its mega_keywords attribute updated "
            "with an expected value surrounded by spaces.")
    assert transformed_product.mega_keywords == (
        " "
        + new_product_name
        + (" pack 8 pieces 2kg farine et 33cl soda the brand the generic name of "
            "the product category_1, category_2 these are keywords 5012345678912"
            " "))


def test_fetch_all_categories_from_products():

    first_product = copy.deepcopy(good_downloaded_product_as_object)
    second_product = copy.deepcopy(first_product)

    first_product.categories = ["cat1", "cat3", "", "cat5"]
    second_product.categories = ["cat1", "cat2", "cat4", "cat5"]

    print("No list to analyze should return an empty set")
    assert SUT.fetch_all_categories_from_products(None) == set()

    print("List of elements that are not instance of WellFormedProduct should return "
            "an empty set")
    assert SUT.fetch_all_categories_from_products(
        ["not", "instance", "of", "WellFormedProduct"]) == set()

    print("List of pruducts should return one set of all of their categories if not empty "
            "so that each category appears only once")
    assert SUT.fetch_all_categories_from_products([first_product, second_product]) == (
        {"cat1", "cat2", "cat3", "cat4", "cat5"})
