import logging

import pytest

from src.products.management.commands.addproducts import Command


SUT = Command

right_list_of_args = ["10", "boisson", "20", "any"]
wrong_list_of_args = ["boisson", "10", "any", "20"]
list_of_args_as_str = ""


def test_check_if_args_well_formed(monkeypatch, caplog):
    caplog.set_level(logging.INFO)

    def mock_download_products(quantity_of_products, keyword):
        print("Dans le mock download products")
        return [
            {"name": "product1", "categories": "category1, category2"},
            {"name": "product", "categories": "category1, category2"}]

    def mock_populate_database(all_products, all_categories):
        print("Dans le mock_populate_database")
        return True

    def mock_fetch_all_categories_from_products():
        print("Dans le mock_fetch_all_categories_from_products")
        return set(["category1", "category2"])

    monkeypatch.setattr("src.products.etl_extract.download_products",
                        mock_download_products)

    monkeypatch.setattr("src.products.etl_transform.fetch_all_categories_from_products",
                        mock_fetch_all_categories_from_products)

    monkeypatch.setattr("src.products.etl_load.populate_database",
                        mock_populate_database)

    print("If the last value in the cli is not a number, then should return None "
            "because no problem occurred")
    assert SUT._check_if_args_well_formed(
        SUT, {'list_of_args': right_list_of_args}) == None

    print("If the las value in the cli is a number then an exception is raised.")
    with pytest.raises(Exception):
        SUT._check_if_args_well_formed(SUT, {'list_of_args': right_list_of_args + "24"})

    print("If the args in the the cli is not as follows: int string int string "
            "(eg: 10 boisson 20 any), then should raise an exception")
    with pytest.raises(Exception):
        SUT._check_if_args_well_formed(SUT, {'list_of_args': wrong_list_of_args})


def test_add_arguments():

    class MockParser:
        def add_argument(word_list_of_args, nargs):
            if nargs == "+" and word_list_of_args == "list_of_args":
                return None
            else:
                raise Exception("The args of add_argument must be: 'list_of_args', nargs='+'")

    parser = MockParser

    print("Add_argument method should have <<'list_of_args'>> and <<nargs='+'>> as arguments")
    assert SUT.add_arguments(SUT, parser) == None
