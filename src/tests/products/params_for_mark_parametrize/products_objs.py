import copy

from src.products.utils import (
    WellFormedProduct)
from src.tests.products.params_for_mark_parametrize.params_etl_extract import (good_downloaded_product)


good_downloaded_product_obj = WellFormedProduct(good_downloaded_product)

dl_product1 = copy.deepcopy(good_downloaded_product_obj)
dl_product1.code = 1012345678111
dl_product1._id = 1000000001
dl_product1.categories = ["cat1", "cat2", "cat3"]

dl_product2 = copy.deepcopy(good_downloaded_product_obj)
dl_product2.code = 2012345678222
dl_product1._id = 2000000002
dl_product1.categories = ["cat3", "cat4", "cat5"]

product1 = copy.deepcopy(dl_product1)
product2 = copy.deepcopy(dl_product1)
product3 = copy.deepcopy(dl_product1)
product4 = copy.deepcopy(dl_product1)
product5 = copy.deepcopy(dl_product1)

product1._id = "123456"
product1.nutriscore_grade = "d"
product1.product_name_fr = "Lemonade"
product1.mega_keywords = " lemonade lemon beverage "
product1.categories = ["beverage", "sugar added", "fruity", "lemon", "carbonated water"]

product2._id = "123457"
product2.nutriscore_grade = "e"
product2.product_name_fr = "Cool cola"
product2.mega_keywords = " cool cola soda beverage cola "
product2.categories = ["beverage", "sugar added", "cola"]

product3._id = "123458"
product3.nutriscore_grade = "b"
product3.product_name_fr = "Lemonade light"
product3.mega_keywords = " lemonade lemon beverage light"
product3.categories = ["beverage", "fruity", "lemon", "light", "carbonated water"]

product4._id = "123459"
product4.nutriscore_grade = "c"
product4.product_name_fr = "Cool cola light"
product4.mega_keywords = " cool cola soda beverage cola light "
product4.categories = ["beverage", "cola", "light"]

product5._id = "123460"
product5.nutriscore_grade = "a"
product5.product_name_fr = "Natural carbonated water"
product5.mega_keywords = " carbonated water beverage natural "
product5.categories = ["beverage", "carbonated water", "water"]

welformed_products = [product1, product2, product3, product4, product5]
