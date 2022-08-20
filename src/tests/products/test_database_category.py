import pytest

from products.models import Category

pytestmark = pytest.mark.django_db  # Create a virtual database


class TestCategoryModel:

    def add_a_category(self):
        return Category.objects.create(name="Category name")

    def test_should_add_a_category_to_the_db(self):
        category = self.add_a_category()

        assert category.name == "Category name"
        assert Category.objects.all().count() == 1

    def test_should_not_be_able_to_add_the_same_category_to_the_db(self):
        expected = "unique name violation"
        result = "Test failed"

        self.add_a_category()
        try:
            self.add_a_category()
        except Exception as e:

            if "unique" in str(e).lower():
                result = expected

        assert result == expected
