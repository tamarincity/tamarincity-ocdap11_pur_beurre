from concurrent.futures import ThreadPoolExecutor  # Built in module

import requests

from products.etl_transform import transform_product

from products.utils import WellFormedProduct
from products.constants import (
    ETL_EXTRACT_MAX_WORKERS,  # Number of simultaneous requests
    URL_OPEN_FOOD_FACT,
)


def check_fields_of_product(product_downloaded: dict):
    """Check if all required fields of the product are present.
    Returns an instance. Not a dict!!!"""
    if not (product_downloaded and isinstance(product_downloaded, dict)):
        return False
    return WellFormedProduct(product_downloaded)


def get_url(url):
    return requests.get(url).json()


def download_products(required_nbr_of_products: int, keyword):

    if not (
        required_nbr_of_products
        and keyword
        and isinstance(required_nbr_of_products, int)
        and isinstance(keyword, str)
        or required_nbr_of_products < 1
    ):
        return

    page_nbr = -9
    nbr_of_downloaded_products = 0
    while nbr_of_downloaded_products <= required_nbr_of_products:

        page_nbr += ETL_EXTRACT_MAX_WORKERS
        params_as_str = (
            "action=process" "&sort_by=unique_scan_n" "&page_size=20" "&json=1"
        )

        word_to_find_in_product = ""
        if keyword not in ["any", "all"]:
            word_to_find_in_product = (
                "&tagtype_0=categories" "&tag_contains_0=contains" f"&tag_0={keyword}"
            )

        urls = [
            f"{URL_OPEN_FOOD_FACT}?{params_as_str}{word_to_find_in_product}"
            f"&page={page_nbr+i}"
            for i in range(ETL_EXTRACT_MAX_WORKERS)
        ]
        nbr_of_empty_response = 0
        with ThreadPoolExecutor(max_workers=ETL_EXTRACT_MAX_WORKERS) as pool:

            list_of_responses = list(pool.map(get_url, urls))

        for res in list_of_responses:
            if res:
                product_not_found = not res.get("products", None)
                if product_not_found:
                    nbr_of_empty_response += 1
                    continue

                for downloaded_product in res["products"]:

                    verified_product = check_fields_of_product(downloaded_product)
                    if not (verified_product and verified_product.is_valid):
                        continue

                    modified_product = transform_product(verified_product)
                    if not modified_product:
                        continue

                    nbr_of_downloaded_products += 1

                    if nbr_of_downloaded_products > required_nbr_of_products:
                        return
                    # Ci-dessous, "yield" est comme un "return" sauf qu'il revient ici une fois que la fonction
                    # qui en a besoin a terminé. Ainsi, la boucle continue.
                    # L'objet généré par un yield est un générateur. Il peut être converti en liste.
                    yield modified_product

        if nbr_of_empty_response >= ETL_EXTRACT_MAX_WORKERS:

            return
