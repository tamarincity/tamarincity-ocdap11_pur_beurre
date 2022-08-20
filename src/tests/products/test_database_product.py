import pytest

from products.models import Category
from products.models import Product

pytestmark = pytest.mark.django_db  # Create a virtual database


class TestDatabase:

    def add_a_category(self):
        return Category.objects.create(name="Category name")

    def add_a_product(self):
        return Product.objects.create(
            name="Product name",
            brands="brand1, brand2",
            code=8714100614754,
            original_id=9876543210,
            quantity="Quantity 1.5l",
            image_thumb_url="url-thumb-image",
            image_url="url-thumb-image",
            ingredients_text="list of ingredients",
            keywords="some keywords (mega key_words)",
            nutriments="Some nutriments",
            nutriscore_grade="Grade (A B C D E)",
            stores="All the stores where you can find the product",
            url="url_of_the_website_of_the_product",
        )

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

    def test_should_add_a_product_to_the_db(self):
        product = self.add_a_product()

        assert product.name == "Product name"
        assert product.brands == "brand1, brand2"
        assert product.code == 8714100614754
        assert product.original_id == 9876543210
        assert product.quantity == "Quantity 1.5l"
        assert product.image_thumb_url == "url-thumb-image"
        assert product.image_url == "url-thumb-image"
        assert product.ingredients_text == "list of ingredients"
        assert product.keywords == "some keywords (mega key_words)"
        assert product.nutriments == "Some nutriments"
        assert product.nutriscore_grade == "Grade (A B C D E)"
        assert product.stores == "All the stores where you can find the product"
        assert product.url == "url_of_the_website_of_the_product"
        assert Product.objects.all().count() == 1

    def test_should_not_be_able_to_add_the_same_product_to_the_db(self):
        expected = "unique original_id violation"
        result = "Test failed"

        self.add_a_product()
        try:
            self.add_a_product()
        except Exception as e:

            if "unique" in str(e).lower():
                result = expected

        assert result == expected
