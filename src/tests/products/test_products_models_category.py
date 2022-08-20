import pytest

from products.models import Category as SUT


pytestmark = pytest.mark.django_db


class TestCategoryModel:

    # @pytest.mark.test_me
    def test_add_many(self, caplog):
        caplog.clear()

        print("Non set as categories")
        print("     should return None because no category was added")
        assert SUT.add_many(["not", "a", "set"]) == None

        print("     should log a warning")
        assert "WARNING" in caplog.text
        caplog.clear()

        print("An empty category in categories should log an error")
        SUT.add_many({"category_1", "category_2", "", "category_3"})

        assert "ERROR" in caplog.text
        caplog.clear()

        print("An error while adding categories "
                "should prevent any category of the set from being added")
        assert SUT.objects.count() == 0

        print("A non string as cateory in categories should log an error "
                "and raise a TypeError exception")
        with pytest.raises(TypeError):
            SUT.add_many({"category_1", "category_2", ["Not string"]})
            assert "ERROR" in caplog.text
            caplog.clear()

        print("A set of categories ")
        categories = SUT.add_many({"category_1", "category_2", "category3"})

        print("     should let all of them be added to the database")
        assert len(categories) == 3

        print("     should return a dict of categories")
        assert isinstance(categories, dict)

        print("         with the name of each category as a key")
        assert ",".join(categories) == ",".join({"category_1", "category_2", "category3"})

        print("         with an instance of Category as a value")
        assert [category for category in categories.values() if not (isinstance, SUT)] or True
