import copy


downloaded_product_with_a_missing_field = {
    "_id": 12345,
    "_keywords": ["these", "are", "keywords"],
    "brands": "The Brand marque",
    "categories_old": "category_1, category_2",
    "code": 5012345678912,
    "generic_name_fr": "the generic name of the product",
    "image_thumb_url": "im-the-thumb-url",
    "image_url": "im-the-image-url",
    "ingredients_text_fr": "ingredient1, ingredient2, and ingredient3",
    "lang": "fr",
    "nutriments": {"nutriment1": "5", "nutriment2": "20"},
    "nutriscore_grade": "A",
    "pnns_groups_1": "beverage",
    "product_name_fr": "Name Of The Product",
    "quantity": "Pack de 8 pieces de 2 Kg de farine & 330ml de SODA",
    "stores": "Mag1, Mag2, Mag3",
    "stores_tags": ["Mag1", "Mag2", "Mag3"],
}


good_downloaded_product = copy.deepcopy(downloaded_product_with_a_missing_field)
# Add the missing field "url"
good_downloaded_product["url"] = "official-url-of-product"
downloaded_product_with_an_empty_value = copy.deepcopy(good_downloaded_product)
downloaded_product_with_an_empty_value["brands"] = ""
