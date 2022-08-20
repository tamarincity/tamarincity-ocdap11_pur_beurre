from dataclasses import dataclass

import pytest
import requests

from src.products import etl_extract
from src.products.etl_extract import (
    check_fields_of_product,
    download_products,
    get_url,
    WellFormedProduct,
)

from products.constants import (
    ETL_EXTRACT_MAX_WORKERS,
    URL_OPEN_FOOD_FACT,
)

from params_for_mark_parametrize.params_etl_extract import (
    good_downloaded_product,
    downloaded_product_with_a_missing_field,
    downloaded_product_with_an_empty_value
)


@pytest.mark.parametrize(
    "arg_explanation, what_should_happen, downloaded_product, expected_value",
    [
        ("Well formed downloading product",
            "Should return a instance of WellFormedProduct with the 'is_valid' property = True",
            good_downloaded_product,
            True),
        ("Downloaded product with a missing required field",
            "Should return a instance of WellFormedProduct with the 'is_valid' property = False",
            downloaded_product_with_a_missing_field,
            False),
        ("Downloaded product with a required field that is existing but empty",
            "Should return a instance of WellFormedProduct with the 'is_valid' property = False",
            downloaded_product_with_an_empty_value,
            False),
        ("None as downloaded product",
            "Should return False",
            None,
            False),
        ("product_downloaded is not a dict",
            "Should return False",
            ["not", "a", "dict"],
            False)])
def test_check_fields_of_product(
        arg_explanation,
        what_should_happen,
        downloaded_product,
        expected_value):

    print(arg_explanation, " ", what_should_happen)
    product = check_fields_of_product(downloaded_product)
    if (downloaded_product
            and isinstance(downloaded_product, dict)):

        assert isinstance(product, WellFormedProduct)
        assert product.is_valid == expected_value
    else:
        assert product == expected_value


def test_get_url():
    print("url is empty should raise exception: requests.exceptions.MissingSchema")
    with pytest.raises(requests.exceptions.MissingSchema):  # equiv to assert for exceptions
        get_url("")

    print("url is not a string should raise exception: requests.exceptions.MissingSchema")
    with pytest.raises(requests.exceptions.MissingSchema):
        get_url({"message", "not a string"})

    print("Wrong endpoint should raise exception: requests.exceptions.JSONDecodeError")
    with pytest.raises(requests.exceptions.JSONDecodeError):
        get_url("https://fr.openfoodfacts.org/cgi/search.pl")

    print("Correct url should return json of products")
    assert "products" in get_url(
        "https://fr.openfoodfacts.org/cgi/search.pl"
        "?action=process&sort_by=unique_scan_n&page_size=5&json=1")


class TestDownloadProducts():

    # The first group of requests is the set of the first request of each worker
    # If there are 10 workers then for the first group of requests, the the
    # param "page" of the url should be "page=1" for the 1st worker ..."page=10"
    # for the last worker
    # In the second group of requests, the param "page" of the url should be
    # "page=11"... "page=20" etc.
    is_first_page_in_first_group_of_request = False
    is_any_page_of_second_group_of_request = False

    def test_download_products(self, monkeypatch):

        # params of the function download_products()
        positive_required_nbr_of_products = 15
        required_nbr_of_products_is_null = 0
        required_nbr_of_products_is_negative = -15

        keyword = "a keyword"
        no_keyword = None
        keyword_is_not_string = ["A keywor in a list"]
        no_products_returned = 0

        def mock_get_url(url):

            if URL_OPEN_FOOD_FACT in url and "&page=1" in url:
                self.is_first_page_in_first_group_of_request = True
            if URL_OPEN_FOOD_FACT in url and f"&page={ETL_EXTRACT_MAX_WORKERS + 1}" in url:
                self.is_any_page_of_second_group_of_request = True
            if (self.is_first_page_in_first_group_of_request == True
                    and self.is_first_page_in_first_group_of_request == True):

                return {"products": [good_downloaded_product, downloaded_product_with_an_empty_value]}

        def mock_check_fields_of_product(product_downloaded):

            # Create an instance from a dict
            @dataclass(frozen=False)
            class WellFormedProductForTests_:
                def __init__(self, product_downloaded):
                    for field, value in product_downloaded.items():
                        setattr(self, field, value)
                    setattr(self, "is_valid", False)

                    if product_downloaded == good_downloaded_product:
                        setattr(self, "is_valid", True)

            return WellFormedProductForTests_(product_downloaded)

        def mock_transform_product(verified_product):
            setattr(verified_product, "categories", ["category1", "category2"])
            setattr(verified_product, "mega_keywords", "mega keywords")
            return verified_product

        monkeypatch.setattr(etl_extract, "get_url", mock_get_url)
        monkeypatch.setattr(etl_extract, "check_fields_of_product", mock_check_fields_of_product)
        monkeypatch.setattr(etl_extract, "transform_product", mock_transform_product)

        print("Positive required nbr of products")
        print("     should return the required nbr of products")
        assert (
            len(list(download_products(positive_required_nbr_of_products, keyword)))
            == positive_required_nbr_of_products)

        print("     should return only well formed products")
        for product in list(download_products(positive_required_nbr_of_products, keyword)):
            assert product.is_valid == True

        print("     should return only modified products")
        for product in list(download_products(positive_required_nbr_of_products, keyword)):
            assert product.mega_keywords == 'mega keywords'
            assert product.categories == ["category1", "category2"]

        print("Zero required nbr of products should return zero product")
        assert (
            len(list(download_products(required_nbr_of_products_is_null, keyword)))
            == no_products_returned)

        print("Negative required nbr of products should return zero product")
        assert (
            len(list(download_products(required_nbr_of_products_is_negative, keyword)))
            == no_products_returned)

        print("No keyword should return zero product")
        assert (
            len(list(download_products(positive_required_nbr_of_products, no_keyword)))
            == no_products_returned)

        print("Non string keyword should return zero product")
        assert (
            len(list(download_products(positive_required_nbr_of_products, keyword_is_not_string)))
            == no_products_returned)
