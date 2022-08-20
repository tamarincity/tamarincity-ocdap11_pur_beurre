import logging

from django.core.management.base import BaseCommand, CommandError

from products.etl_extract import download_products
from products.etl_transform import fetch_all_categories_from_products
from products.etl_load import populate_database


class Command(BaseCommand):
    help = (
        "Download products from Open Food Facts API "
        '(command: addproducts 100 boisson 50 "pate a tartiner")'
    )

    def add_arguments(self, parser):
        parser.add_argument("list_of_args", nargs="+")

    def _check_if_args_well_formed(self, options: dict):

        # The last arg must not be an integer
        try:
            int(options["list_of_args"][-1])
            raise Exception(
                "command must be: function int str int str "
                "(e.g.: addproducts 100 boissons 50 petit-dejeuners)"
            )
        except Exception as e:

            if "invalid literal" in str(e):
                logging.info(
                    "The last argument of the command is probably OK (not an integer)"
                )
            else:
                raise CommandError(str(e))

        # parse args
        for i, arg in enumerate(options["list_of_args"]):

            # Get the number of products to download
            if i % 2 == 0:
                try:
                    # arg must be an integer
                    arg = int(arg)
                except Exception:
                    raise CommandError(
                        "command must be: function int str int str "
                        "(e.g.: addproducts 100 boissons 50 petit-dejeuners)"
                    )

            # Get the kind of products to download (e.g.: "pate a tartiner")
            if i % 2 != 0 and not isinstance(arg, str):
                try:
                    # arg must be a string
                    arg = int(arg)
                    raise CommandError(
                        "command must be: function int str int str "
                        "(e.g.: addproducts 100 boissons 50 petit-dejeuners)"
                    )
                except Exception:
                    pass

    def handle(self, *args, **options):
        print("options: ", options)

        self._check_if_args_well_formed(options)

        all_products = []
        for i, arg in enumerate(options["list_of_args"]):
            if i % 2 != 0:
                try:
                    quantity_of_products = int(options["list_of_args"][i - 1])
                    keyword = arg
                    print()
                    self.stdout.write(
                        f"Downloading: {quantity_of_products} %s" % keyword + "..."
                    )

                    downloaded_products_as_generator = download_products(
                        quantity_of_products, keyword
                    )

                    downloaded_products = list(downloaded_products_as_generator)

                    nbr_of_valid_products = len(downloaded_products)

                    print("Nbr of valid products: ", nbr_of_valid_products)

                except Exception as e:

                    raise CommandError(str(e))

                if nbr_of_valid_products == 0:
                    self.stdout.write(
                        self.style.ERROR("No products to download for %s" % keyword)
                    )
                else:
                    all_products += downloaded_products
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully downloaded "{quantity_of_products} %s"' % arg
                        )
                    )

        print()
        self.stdout.write(self.style.SUCCESS("-------------------------------------"))
        self.stdout.write(
            self.style.SUCCESS("The download of the products is now complete!")
        )
        print()

        if all_products:
            print("Total nbr of downloaded products: ", len(all_products))
        else:
            print("No product found !")

        print("Fetching all categories from downloaded products...")
        all_categories = fetch_all_categories_from_products(all_products)
        print("Done!")

        print("Loading products to the database...")
        is_database_populated = populate_database(all_products, all_categories)
        if is_database_populated and all_products:
            self.stdout.write(
                self.style.SUCCESS("The database has been populated with success!")
            )
            print()
        else:
            self.stdout.write(self.style.ERROR("No products added to the database!"))
            print()
