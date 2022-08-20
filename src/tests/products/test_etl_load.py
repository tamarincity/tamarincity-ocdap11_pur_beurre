from products.models import Category, Product
from src.products import etl_load
from products.utils import WellFormedProduct

product1 = WellFormedProduct({
    "_id": 123456,
    "_keywords": ["one", "product"],
    "brands": "great brand",
    "categories": ["category1", "category2"],
    "categories_old": "category1, category2",
    "code": 12345678,
    "generic_name_fr": "My product name 1",
    "image_thumb_url": "url/of/thumb1",
    "image_url": "url/of/image1",
    "ingredients_text_fr": "igredient1, ingredient2",
    "lang": "fr",
    "mega_keywords": "one product great brand 12345678 my name 1",
    "nutriments": {"salt_for_100g": 0.1, "sugar_for_100g": 1},
    "nutriscore_grade": "c",
    "pnns_groups_1": "beverage",
    "product_name_fr": "My product name 1",
    "quantity": "50cl",
    "stores": "Geant",
    "stores_tags": "geant, casino",
    "url": "openfoodfact/url/of/product1",
})

product2 = WellFormedProduct({
    "_id": 123456,
    "_keywords": ["second", "product"],
    "brands": "super brand",
    "categories": ["category2", "category3"],
    "categories_old": "category2, category3",
    "code": 9876543,
    "generic_name_fr": "My product name 2",
    "image_thumb_url": "url/of/thumb2",
    "image_url": "url/of/image2",
    "ingredients_text_fr": "igredient1, ingredient2",
    "lang": "fr",
    "mega_keywords": "second product super brand 9876543 my name 2",
    "nutriments": {"salt_for_100g": 0, "sugar_for_100g": 0.5},
    "nutriscore_grade": "b",
    "pnns_groups_1": "beverage",
    "product_name_fr": "My product name 2",
    "quantity": "50cl",
    "stores": "Leader Price",
    "stores_tags": "leader, price",
    "url": "openfoodfact/url/of/product2",
})

list_of_welformed_products = [product1, product2]


def test_populate_database(monkeypatch):

    SUT = etl_load
    is_categories_added = True

    def mock_category_add_many(categories):
        if not (categories
                and isinstance(categories, set)):
            return False
        for category in categories:
            if not isinstance(category, str):
                return False

        return True

    def mock_product_add_many(products):
        if not (is_categories_added
                and products
                and isinstance(products, list)):
            return False

        for product in products:
            if not isinstance(product, WellFormedProduct):
                return False

        return True

    monkeypatch.setattr(Category, 'add_many', mock_category_add_many)
    monkeypatch.setattr(Product, 'add_many', mock_product_add_many)

    print("A list of WellFormedProduct and a set of categories "
            "should return True")
    assert SUT.populate_database(
        list_of_welformed_products,
        set(["category1", "category2", "category3"])) == True

    print("A list of non-Welformed product as products should return False because "
            "The products can't be added.")
    assert SUT.populate_database(
        [{"name": "product1"}, {"name": "product2"}],
        set(["category1", "category2", "category3"])) == False

    print("Non-set as categories should return False because "
            "The products can't be added. They cannot be associated with their categories")
    assert SUT.populate_database(
        [{"name": "product1"}, {"name": "product2"}],
        None) == False
