import logging

from products import utils
from products.utils import (
    format_quantity_and_unit,
    format_text,
    remove_space_between_quantity_and_unit,
)


def test_remove_space_between_quantity_and_unit(caplog):
    print("""Empty string as text to modify should return an empty string
    and log an error.""")
    assert remove_space_between_quantity_and_unit("") == ""
    assert "ERROR" in caplog.text

    print(print("""None as text to modify should return an empty string
    and log an error."""))
    assert remove_space_between_quantity_and_unit(None) == ""
    assert "ERROR" in caplog.text

    print(print("""A text which is not a string should return an empty string
    and log an error."""))
    assert remove_space_between_quantity_and_unit(["Text", "is", "not", "string"]) == ""
    assert "ERROR" in caplog.text

    quantities = (
        "1 L, 10KG,5 L,8 mm³, 20 KG, 30 Kg 2 cm³ 2,8 l 2.9 cl 2 ml 2 hl 2 dl 2 g 2 Kg 2 kg "
        "2 mm 2 cm 2 dm 2 m2 2 m²,2 M² 2 m3 2 m³ 2 cm2 2 cm² 2 cm3 2 cm³ 2 mm2 2 mm² "
        "2 mm3 2 mm³")

    expected = (
        ' 1l,  10kg,5l, 8mm³,  20kg,  30kg 2cm³ 2,8l 2.9cl 2ml 2hl 2dl 2g 2kg '
        '2kg 2mm 2cm 2dm 2m2 2m², 2m² 2m3 2m³ 2cm2 2cm² 2cm3 2cm³ 2mm2 2mm² 2mm3 2mm³ ')
    print(f"<<{quantities}>>")
    print(f"should return <<{expected}>>.")
    assert remove_space_between_quantity_and_unit(quantities) == expected


text_to_modify = (
    "Orange Juice 1,5 L soda 330 ml 0,5 L sugar 0,3 KG "
    "corn Flakes 300 grammes 2 kilogrammes 1 KILOGRAMME milk 1 l"
    " au à a la le aux en et de des du marque: marques: brands: code: "
    "marque:marques:brands:code:80123456789 marques brands code marque ")


def test_format_quantity_and_unit(monkeypatch, caplog):

    expected = (
        " "
        "orange juice 1.5l soda 33cl 50cl sugar 300g corn flakes 300g 2kg 1kg milk 1l "
        "au à a la le aux en et de des du marque: marques: brands: "
        "code: marque:marques:brands:code:80123456789 marques brands code marque"
        " ")

    def mock_remove_space_between_quantity_and_unit(text_as_arg):
        if not (text_as_arg
                and isinstance(text_as_arg, str)):

            logging.error("""Error in utils.remove_space_between_quantity_and_unit().
            the arg (text to modify) should be a string and should not be empty.""")
            return ""

        if text_as_arg == (
                "Orange Juice 1,5 L soda 330 ml 0,5 L sugar 0,3 KG "
                "corn Flakes 300 grammes 2 kilogrammes 1 KILOGRAMME milk 1 l"
                " au à a la le aux en et de des du marque: marques: brands: code: "
                "marque:marques:brands:code:80123456789 marques brands code marque "):

            return expected

        return "This test with this arg has not been covered yet !"

    monkeypatch.setattr(
        utils,
        "remove_space_between_quantity_and_unit",
        mock_remove_space_between_quantity_and_unit)

    print(f"<<{text_to_modify}>>")
    print(f"should return <<{expected}>>")
    assert format_quantity_and_unit(text_to_modify) == expected

    print("Empty string should return empty string and log an error")
    assert format_quantity_and_unit("") == ""
    assert "ERROR" in caplog.text

    print("Non string text should return empty string and log an error")
    assert format_quantity_and_unit({"text": "is dict"}) == ""
    assert "ERROR" in caplog.text


def test_format_text(monkeypatch, caplog):

    expected = (
        " "
        "orange juice 1.5l soda 33cl 50cl sugar 300g corn flakes 300g 2kg 1kg milk 1l 80123456789"
        " ")

    def mock_format_quantity_and_unit(text):
        if not (text
                and isinstance(text, str)):
            logging.error(
                "Error in format_quantity_and_unit! "
                "Text to modify should be a string")
            return ""

        print("Expected arg in format_quantity_and_unit: ", text)
        if text == (
                "orange juice 1,5 l soda 330 ml 0,5 l sugar 0,3 kg corn flakes 300 "
                "grammes 2 kilogrammes 1 kilogramme milk 1 l 80123456789"):
            return expected

        return "This test with this arg has not been covered yet !"

    monkeypatch.setattr(utils, "format_quantity_and_unit", mock_format_quantity_and_unit)

    assert format_text(text_to_modify) == expected

    print("Empty string should return empty string and log an error")
    assert format_quantity_and_unit("") == ""
    assert "ERROR" in caplog.text

    print("Non string text should return empty string and log an error")
    assert format_quantity_and_unit({"text": "is dict"}) == ""
    assert "ERROR" in caplog.text
