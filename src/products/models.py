import logging
import ast

from django.db import connection, models
from django.db import transaction
from django.db.models import Q

from accounts.models import Customer

from products.utils import WellFormedProduct
from .constants import (
    MAX_NBR_OF_SUBSTITUTE_PRODUCTS,
    PRODUCT_NAME_MAX_LENGTH,
    QUANTITY_MAX_LENGTH,
)


# Create your models here.


class Product(models.Model):
    name = models.CharField(
        max_length=PRODUCT_NAME_MAX_LENGTH, help_text="Name of the product"
    )
    brands = models.TextField(help_text="Brands of the product")
    code = models.BigIntegerField(help_text="Bar code of the product")
    original_id = models.BigIntegerField(unique=True, db_index=True)
    quantity = models.CharField(max_length=QUANTITY_MAX_LENGTH)
    image_thumb_url = models.URLField()
    image_url = models.URLField()
    ingredients_text = models.TextField()

    # keywords = (" "
    #       + product_name_fr
    #       + quantity
    #       + brands
    #       + generic_name_fr
    #       + categories_old
    #       + keywords_as_list
    #       + str(code)
    #       + " ")
    keywords = models.TextField()

    # nutriments_100g = these to string =>(
    # nutriments["energy-kcal"], nut..["fat_100g"], ["fat_unit"], ["fiber_100g"], ["fiber_unit"],
    # ["proteins_100g"], ["proteins_unit"], ["salt_100g"], ["salt_unit"], ["sugar_100g"], ["sugar_unit"])
    nutriments = models.JSONField()
    nutriscore_grade = models.CharField(max_length=2)
    stores = models.TextField()
    url = models.URLField()

    # Metadata
    class Meta:
        ordering = ["name"]

    # Methods
    def __str__(self):
        return self.name

    @classmethod
    def add_many(cls, products: list[WellFormedProduct]) -> bool:
        """Add products to the database then return True if they were added successfully
        otherwise False.
        The arg products is a list of instances of WellFormedProduct."""

        if not (products and isinstance(products, list)):
            return False

        is_new_product_added = False
        try:
            with transaction.atomic():  # Commit only if all queries have been done with success
                for product in products:
                    try:
                        stored_product = Product.objects.get(original_id=product._id)
                    except Product.DoesNotExist:  # if the product is not already stored
                        is_new_product_added = True
                        stored_product = Product(
                            brands=product.brands,
                            code=product.code,
                            image_thumb_url=product.image_thumb_url,
                            image_url=product.image_url,
                            ingredients_text=product.ingredients_text_fr,
                            keywords=product.mega_keywords,
                            name=product.product_name_fr,
                            nutriments=product.nutriments,
                            nutriscore_grade=product.nutriscore_grade,
                            original_id=product._id,
                            quantity=product.quantity,
                            stores=product.stores,
                            url=product.url,
                        )
                        stored_product.save()
                    except Exception as e:
                        raise Exception(str(e))

                    for category in product.categories:
                        stored_category = Category.objects.get(name=category)
                        stored_category.products.add(stored_product)

            if not is_new_product_added:
                print("No new product added to the database!")
            return True
        except Exception as e:
            logging.error("Error adding products. Exception was: %s", e)
            return False

    @classmethod
    def find_original_products(cls, keywords: str):
        """Get products by keywords.
        All the keywords must be in product.keywords for the product to get selected.
        return: list of products
        """
        if not (keywords and isinstance(keywords, str)):
            return None

        keywords = keywords.replace(",", " ")
        keywords_as_list = keywords.split()

        # First element of the params
        params = Q(keywords__icontains=keywords_as_list[0])
        # Add all of the the other params to make the query to the db
        for keyword in keywords_as_list[1:]:
            params &= Q(keywords__icontains=keyword)

        products = Product.objects.filter(params)
        return products

    @classmethod
    def find_substitute_products(
        cls, original_product_id: str, original_product_nutriscore: str
    ):
        """Returns a list of substitute products for a given product id.
        The products will be selected according to the number of categories in common
        with the original one then according to their nutriscore_grade (A to E).
        """

        if not (
            original_product_id
            and original_product_nutriscore
            and isinstance(original_product_id, str)
            and isinstance(original_product_nutriscore, str)
        ):

            raise Exception(
                "original_product_id and original_product_nutriscore must be "
                "strings and not empty"
            )

        try:
            int(original_product_id)
        except ValueError:
            raise Exception(
                "Error in products.models.Product.find_substitute_products()! "
                "original_product_id must be convertible to integer!"
            )

        try:
            int(original_product_nutriscore)
            raise Exception(
                "Error in products.models.Product.find_substitute_products()! "
                "original_product_nutriscore must be ONE letter from a to e!"
            )
        except ValueError:
            if len(original_product_nutriscore) != 1:
                raise Exception(
                    "Error in products.models.Product.find_substitute_products()! "
                    "original_product_nutriscore must be ONE letter from a to e!"
                )

        product_fields_as_str = (
            "p.id,"
            "p.name,"
            "p.brands,"
            "p.code,"
            "p.original_id,"
            "p.quantity,"
            "p.keywords,"
            "p.url,"
            "p.image_url,"
            "p.image_thumb_url,"
            "p.nutriscore_grade,"
            "p.ingredients_text,"
            "p.stores,"
            "p.nutriments,"
        )

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                        SELECT
                            {product_fields_as_str}
                    """
                    " %s"
                    """,
                            COUNT(product_id) AS weight
                        from
                            products_product p
                        inner join
                            products_category_products
                            on p.id = product_id
                        where
                            category_id in (select cp.category_id from products_product p
                                        inner join products_category_products cp
                                            on p.id = cp.product_id
                                        where p.id =
                    """
                    " %s"
                    """)
                            and nutriscore_grade <
                    """
                    "  %s"
                    f"""
                        GROUP BY
                             {product_fields_as_str}
                            product_id
                        ORDER BY
                             weight desc,
                            p.nutriscore_grade asc
                        limit
                    """
                    "  %s",
                    [
                        original_product_id,
                        original_product_id,
                        original_product_nutriscore,
                        MAX_NBR_OF_SUBSTITUTE_PRODUCTS,
                    ],
                )

                rows = cursor.fetchall()

            fields = [
                "id",
                "name",
                "brands",
                "code",
                "original_id",
                "quantity",
                "keywords",
                "url",
                "image_url",
                "image_thumb_url",
                "nutriscore_grade",
                "ingredients_text",
                "stores",
                "nutriments",
                "product_to_substitute_id",
                "weight",
            ]

            # Creation of the following:
            # products = [{field1:val1, field2: val2}, {field1:val1, field2: val2}...]
            products = [
                {
                    fields[i]: val
                    if fields[i] != "nutriments"  # "nutriments" is a json into a string
                    else {
                        "nutriment": ast.literal_eval(val)
                    }  # "nutriments" => str to json
                    for i, val in enumerate(product)
                }
                for product in rows
            ]

        except Exception as e:
            logging.error("Error while getting substitute products:")
            logging.error(str(e))
            products = []

        return products


class L_Favorite(models.Model):
    customer = models.ForeignKey(
        Customer, related_name="favorites", on_delete=models.CASCADE
    )
    original_product = models.ForeignKey(
        "Product", related_name="original_products", on_delete=models.CASCADE
    )
    substitute_product = models.ForeignKey(
        "Product", related_name="substitute_products", on_delete=models.CASCADE
    )

    # Methods
    def __str__(self):
        return f"{self.original_product}/{self.substitute_product} ({self.customer})"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    products = models.ManyToManyField("Product", related_name="categories")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @classmethod
    def add_many(
        cls, categories: set
    ) -> dict:  # keys are names, values are instance of Category
        """Add categories to the database and return a dictionary that contains
        each stored category as an object.
        E.g.: stored_categories["Beverage
        If somenthing went wrong, return None"""

        if not (categories and isinstance(categories, set)):
            logging.warning(
                "Categories to add in database must be a set and NOT empty!"
            )
            return None

        stored_categories = {}
        try:
            with transaction.atomic():  # Commit only if all queries have been done with success
                for category in categories:
                    if category and isinstance(category, str):
                        try:
                            stored_categories[
                                category
                            ] = Category.objects.get_or_create(name=category)
                        except Exception as e:
                            raise Exception(str(e))
                    else:
                        raise Exception("Each category must be a string and not empty")

            return stored_categories
        except Exception as e:
            logging.error("Error adding categories. Exception was: %s", e)


class ReceivedMessage(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    is_already_read = models.BooleanField(default=False)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=255)
    message = models.TextField()

    class Meta:
        ordering = ["datetime"]

    def __str__(self):
        return f"{str(self.datetime)[:16]} - {self.email}"
