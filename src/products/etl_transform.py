import logging

from products.utils import WellFormedProduct
from products import utils
from .constants import (
    KIND_OF_BISCUITS,
    PRODUCT_NAME_MAX_LENGTH,
    QUANTITY_MAX_LENGTH,
    UNWANTED_CATEGORIES,
)


def str_to_list(string: str) -> list:
    """Convert string to list using "," as a separator"""

    if not (string and isinstance(string, str)):
        logging.warning("Arg in str_to_list must be a string and not empty!")
        return None

    elements = string.split(",")
    elements = [element.strip().capitalize() for element in elements]

    return elements


def remove_products_with_unwanted_categories(categories: list[str]) -> list[str]:
    if not categories:
        return None
    if not isinstance(categories, list):
        raise TypeError

    categories = [category for category in categories if category]

    for unwanted_category in UNWANTED_CATEGORIES:
        if unwanted_category in categories:

            return None

    return categories


def add_mega_keywords_to_product(product: WellFormedProduct):

    if not (product and isinstance(product, WellFormedProduct)):

        raise Exception(
            "Error in products.etl_transform add_mega_keywords_to_product()"
            ": product must be an instance of WellFormedProduct"
        )

    keywords = " ".join(product._keywords)

    mega_keywords = (
        product.product_name_fr
        + " "
        + product.quantity
        + " "
        + product.brands
        + " "
        + product.generic_name_fr
        + " "
        + product.categories_old
        + " "
        + keywords
        + " "
        + str(product.code)
    )

    mega_keywords = mega_keywords.replace("...", " ")

    mega_keywords = utils.format_text(mega_keywords)
    product.mega_keywords = mega_keywords

    return product


def transform_product(product: WellFormedProduct) -> WellFormedProduct or None:
    """Take a product which is an instance of WellFormedProduct as arg.

    - Replace the attribut categories with another made from categories_old.
        categories_old (str) => categories (list)

    - Cut the value of the attribut product_name_fr if too long
    - Cut the value of the attribut quantity if too long
    - Replace the attribut mega_keyword with a new one made with several attributes
        of the product itself.

    Returns the modified product (or None if something went wrong).
    """
    categories_as_string = (
        product.categories_old.replace("Aliments et boissons ", "")
        .replace(" & ", " et ")
        .replace("&", " et ")
    )

    categories_as_string = " " + categories_as_string + " "

    for biscuit in KIND_OF_BISCUITS:
        if (
            biscuit in product.categories_old
            or biscuit in product._keywords
            or biscuit in product.product_name_fr
        ):

            if "Biscuit " not in categories_as_string:
                categories_as_string += ", Biscuit "
            if "Biscuits " not in categories_as_string:
                categories_as_string += ", Biscuits "

    categories_as_list = str_to_list(categories_as_string)
    if not categories_as_list:
        return None

    categories_as_list = remove_products_with_unwanted_categories(categories_as_list)
    if not categories_as_list:
        return None

    setattr(product, "categories", categories_as_list)
    setattr(product, "categories_old", categories_as_string)

    product = add_mega_keywords_to_product(product)

    if len(product.product_name_fr) > PRODUCT_NAME_MAX_LENGTH:
        product.product_name_fr = (
            product.product_name_fr[: PRODUCT_NAME_MAX_LENGTH - 3] + "..."
        )

    if len(product.quantity) > QUANTITY_MAX_LENGTH:
        product.quantity = product.quantity[: QUANTITY_MAX_LENGTH - 3] + "..."

    return product


def fetch_all_categories_from_products(products: list[WellFormedProduct]) -> set:
    if not (
        products
        and isinstance(products, list)
        and isinstance(products[0], WellFormedProduct)
    ):
        return set()
    return set(
        category for product in products for category in product.categories if category
    )
