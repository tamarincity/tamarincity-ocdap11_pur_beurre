import logging
from dataclasses import dataclass, fields  # Built in modules

from django.utils.text import slugify


@dataclass(init=False)
class WellFormedProduct:  # Model used for each product to get downloaded
    _id: int
    _keywords: list
    brands: str
    categories: list
    categories_old: str
    code: int
    generic_name_fr: str
    image_thumb_url: str
    image_url: str
    ingredients_text_fr: str
    lang: str
    mega_keywords: str
    nutriments: dict
    nutriscore_grade: str
    pnns_groups_1: str
    product_name_fr: str
    quantity: str
    stores: str
    stores_tags: list
    url: str

    def __init__(self, downloaded_product):
        # Add fields to the downloading product to make it conform to this model
        downloaded_product["categories"] = [True]
        downloaded_product["mega_keywords"] = "True"
        downloaded_product["nutriments_100g"] = "True"

        # Below, browse all the attributes of the WellFormedProduct class
        # and put them in a tuple named "model_attributes"
        model_attributes = tuple(field.name for field in fields(self))

        # Add to the created object, the attribute "is_valid" with the value "False".
        setattr(self, "is_valid", False)

        nbr_of_model_attributes_found_in_downloaded_product = 0

        # The attributes of WellFormedProduct must be present in the downloaded product
        # and not empty
        for field, value in downloaded_product.items():
            if (value
                    and field in model_attributes):

                nbr_of_model_attributes_found_in_downloaded_product += 1
                # Assign to the instance of WellFormedProduct (self) a key and its value
                setattr(self, field, value)

            if (nbr_of_model_attributes_found_in_downloaded_product == len(model_attributes)
                    and downloaded_product["lang"] == "fr"):

                # Modify the attribute "is_valid" of the created instance (self)
                # with the new value: True.
                setattr(self, "is_valid", True)


def format_text(text_to_modify):

    text_to_modify = " " + text_to_modify.lower() + " "
    # Remove unwanted words
    text_to_modify = (text_to_modify
                        .replace(" au ", " ")
                        .replace(" à ", " ")
                        .replace(" a ", " ")
                        .replace(" la ", " ")
                        .replace(" le ", " ")
                        .replace(" aux ", " ")
                        .replace(" en ", " ")
                        .replace(" et ", " ")
                        .replace(" de ", " ")
                        .replace(" des ", " ")
                        .replace(" du ", " ")
                        .replace(" marque: ", " ")
                        .replace(" marques: ", " ")
                        .replace(" brands: ", " ")
                        .replace(" code: ", " ")
                        .replace(" marque:", " ")
                        .replace(" marques:", " ")
                        .replace(" brands:", " ")
                        .replace(" code:", " ")
                        .replace(" marques ", " ")
                        .replace(" brands ", " ")
                        .replace(" code ", " ")
                        .replace(" marque ", " "))

    text_to_modify = (text_to_modify
                        .replace(" & ", " et ")
                        .replace("&", " et "))

    text_to_modify = text_to_modify.replace(".", "xxpoointxx")
    text_to_modify = text_to_modify.replace(",", "xxviirgxx")
    text_to_modify = slugify(text_to_modify).replace("-", " ")
    text_to_modify = text_to_modify.replace("xxpoointxx", ".")
    text_to_modify = text_to_modify.replace("xxviirgxx", ",")
    return format_quantity_and_unit(text_to_modify)


def format_quantity_and_unit(text_to_modify):
    """Format quantity.
    - Convert 1000 ml into 1l
    - Convert 1,5 L into 1.5l
    - Convert 330 ml into 33cl
    ...
    """

    if not isinstance(text_to_modify, str):
        logging.error("Error in format_quantity_and_unit! "
                        "Text to modify should be a string")
        return ""

    text_to_modify = remove_space_between_quantity_and_unit(text_to_modify)
    text_to_modify = (text_to_modify
                        .replace(" 0,5l", " 50cl")
                        .replace(" 0.5l", " 50cl")
                        .replace(" 1,5l", " 1.5l")
                        .replace(" 1,25l", " 1.25l")
                        .replace(" 2,5l", " 2.5l")
                        .replace(" 0.75l", " 75cl")
                        .replace(" 0,75l", " 75cl")
                        .replace(" 0.33l", " 33cl")
                        .replace(" 0,33l", " 33cl")
                        .replace(" 250ml", " 25cl")
                        .replace(" 330ml", " 33cl")
                        .replace(" 500ml", " 50cl")
                        .replace(" 600ml", " 60cl")
                        .replace(" 750ml", " 75cl")
                        .replace(" 1000ml", " 1l")
                        .replace(" 1500ml", " 1.5l")
                        .replace(" 0.2kg", " 200g")
                        .replace(" 0,2kg", " 200g")
                        .replace(" 0.3kg", " 300g")
                        .replace(" 0,3kg", " 300g")
                        .replace(" 0.5kg", " 500g")
                        .replace(" 0,5kg", " 500g")
                        .replace(" 0.75kg", " 750g")
                        .replace(" 0,75kg", " 750g")
                        .replace(" gramme ", "g ")
                        .replace(" grammes ", "g ")
                        .replace(" grame ", "g ")
                        .replace(" grames ", "g ")
                        .replace(" gram ", "g ")
                        .replace(" grams ", "g ")
                        .replace(" litre ", "l ")
                        .replace(" litres ", "l ")
                        .replace(" kilogramme ", "kg ")
                        .replace(" kilogrammes ", "kg ")
                        .replace(" kilogrames ", "kg ")
                        .replace(" kilogrammes ", "kg ")
                        .replace(" liter ", "l ")
                        .replace(" liters ", "l "))
    return text_to_modify


def remove_space_between_quantity_and_unit(text_to_modify: str) -> str:

    if not (text_to_modify
                and isinstance(text_to_modify, str)):
        logging.error("""Error in utils.remove_space_between_quantity_and_unit().
        the arg (text to modify) should be a string and should not be empty.""")
        return ""
    text_to_modify = text_to_modify.lower()
    text_to_modify = text_to_modify.strip()
    text_to_modify = " " + text_to_modify + " "
    return (text_to_modify
            .replace(" l ", "l ")
            .replace(" cl ", "cl ")
            .replace(" ml ", "ml ")
            .replace(" hl ", "hl ")
            .replace(" dl ", "dl ")
            .replace(" g ", "g ")
            .replace(" kg ", "kg ")
            .replace(" kg ", "kg ")
            .replace(" mm ", "mm ")
            .replace(" cm ", "cm ")
            .replace(" dm ", "dm ")
            .replace(" m2 ", "m2 ")
            .replace(" m² ", "m² ")
            .replace(" m3 ", "m3 ")
            .replace(" m³ ", "m³ ")
            .replace(" cm2 ", "cm2 ")
            .replace(" cm² ", "cm² ")
            .replace(" cm3 ", "cm3 ")
            .replace(" cm³ ", "cm³ ")
            .replace(" mm2 ", "mm2 ")
            .replace(" mm² ", "mm² ")
            .replace(" mm3 ", "mm3 ")
            .replace(" mm³ ", "mm³ ")
            .replace(" l,", "l, ")
            .replace(" cl,", "cl, ")
            .replace(" ml,", "ml, ")
            .replace(" hl,", "hl, ")
            .replace(" dl,", "dl, ")
            .replace(" g,", "g, ")
            .replace(" kg,", "kg, ")
            .replace(" kg,", "kg, ")
            .replace(" mm,", "mm, ")
            .replace(" cm,", "cm, ")
            .replace(" dm,", "dm, ")
            .replace(" m2,", "m2, ")
            .replace(" m²,", "m², ")
            .replace(" m3,", "m3, ")
            .replace(" m³,", "m³, ")
            .replace(" cm2,", "cm2, ")
            .replace(" cm²,", "cm², ")
            .replace(" cm3,", "cm3, ")
            .replace(" cm³,", "cm³, ")
            .replace(" mm2,", "mm2, ")
            .replace(" mm²,", "mm², ")
            .replace(" mm3,", "mm3, ")
            .replace(" mm³,", "mm³, "))
