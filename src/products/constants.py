ETL_EXTRACT_MAX_WORKERS = 10
KIND_OF_BISCUITS = [
                    "Biscuits", "Biscuit",
                    "biscuits", "biscuit",
                    "Boudoirs", "Boudoir",
                    "boudoirs", "boudoir",
                    "Gaufres", "Gaufre",
                    "gaufres", "gaufre",
                    "Gaufrettes", "Gaufrette",
                    "gaufrettes", "gaufrette"]

MAX_NBR_OF_SUBSTITUTE_PRODUCTS = 10
NBR_OF_PAGES = 4
PAGE_NBR_FOR_EXTRACTION_FILENAME = 'page_nbr.txt'
PRODUCT_NAME_MAX_LENGTH = 50
PRODUCTS_PER_PAGE = 20  # ====== Should be reset to 50
QUANTITY_MAX_LENGTH = 30
REQUIRED_FIELDS_OF_A_PRODUCT = (
                                "_id,"
                                "product_name_fr,"
                                "quantity,"
                                "brands,"
                                "ingredients_text_fr,"
                                "nutriscore_grade,"
                                "nutriments,"
                                "pnns_groups_1,"
                                "image_thumb_url,"
                                "image_url,"
                                "stores,"
                                "stores_tags,"
                                "categories_old,"
                                "url,"
                                "lang,"
                                "generic_name_fr,"
                                "code,"
                                "_keywords")

UNWANTED_CATEGORIES = [
                        "Alimentos",
                        "Aperitivos",
                        "Artificially Sweetened Beverages",
                        "Babeurres",
                        "Bebidas",
                        "Beverages",
                        "Bevande",
                        "Breads",
                        "Breakfasts",
                        "Canned",
                        "Chocolate powders",
                        "Cibi ",
                        "Cibo",
                        "Coleslaw",
                        "Common Beans",
                        "Crisp",
                        "Diet Beverages",
                        "Diet Cola Soft Drink",
                        "Dorrobst",
                        "Dranken",
                        "Dry ",
                        "Dry Pastas",
                        "Durum Wheat Pasta",
                        "En:50-63-unsalted-vegetable-fat-margarine-type-high-in-omega-3",
                        "En:breakfasts",
                        "En:cereals-and-potatoes",
                        "En:cereals-and-their-products",
                        "En:cereals-with-fruits",
                        "En:cherry-jams",
                        "En:chocolate-cake-with-melting-centre",
                        "En:fruit-jams",
                        "En:milk-chocolate-biscuits",
                        "En:salty snacks made from potato",
                        "En:uncured-soft-cheese-spreadable-around-30-40-fat-flavoured",
                        "Erdbeere konfitüren",
                        "Farmer",
                        "Fats",
                        "Flavour",
                        "Food",
                        "Frisdranken",
                        "Frucht",
                        "Frucht- und gemüsebasierte lebensmittel",
                        "Fruchtbasierte lebensmittel",
                        "Galletas-con-tableta-de-chocolate",
                        "Getränke",
                        "Getranke",
                        "Getreide",
                        "Gemusebasierte",
                        "Generi Alimentari",
                        "Gezuckerte Getranke",
                        "Gg",
                        "Gluten-Free Breads",
                        "Goat cheeses",
                        "Напитки",
                        "Homogenized milks",
                        "Hot Beverages",
                        "Instant Beverages",
                        "Kaffeegetranke",
                        "Knr Moul Leg Autref 2X1L",
                        "Konfitüren und marmeladen",
                        "Koolzuurhoudende dranken",
                        "Kunstmatig gezoete dranken",
                        "Lebensmittel",
                        "Legume Milks",
                        "Legumes And Their Products",
                        "Legume Seeds",
                        "Light Margarines",
                        "Mandelmilch",
                        "Meals",
                        "Meat Analogues",
                        "Milk chocolate biscuits",
                        "Milk Substitute",
                        "Milks",
                        "Mixes-Of-Squeezed-Fruit-Juices",
                        "Mountain Products",
                        "Mountain Waters",
                        "Napoje Bezalkoholowe",
                        "Nusse Und Nussprodukte",
                        "Nussmilch",
                        "Nuts",
                        "Nuts And Their Products",
                        "Продукты питания",
                        "Pecan Nuts",
                        "Pflanzenmilch",
                        "Pflanzliche brotaufstriche",
                        "Pflanzliche Lebensmittel",
                        "Plantaardige",
                        "Plant-Based Foods",
                        "Plant-Based Foods And Beverages",
                        "Plant-Based Meals",
                        "Plant-Based Spreads",
                        "Plant Milks",
                        "Pomodori E Prodotti Derivati",
                        "Pre-Baked Breads",
                        "Products Without Gluten",
                        "Red Beans",
                        "Salse",
                        "Salted",
                        "Salty snacks",
                        "Shelled",
                        "Snacks salati",
                        "Soft cheeses with bloomy rind",
                        "Soy Milks",
                        "Spaetzle",
                        "Spreadable Fats",
                        "Spreads",
                        "Spring Waters",
                        "Seeds",
                        "Sweetened Beverages",
                        "Thunfische im eigenen saft",
                        "Unpasteurised cheeses",
                        "Unsweetened Beverages",
                        "Unsweetened Natural Soy Milks",
                        "Waters",
                        "De:",
                        "En:",
                        "Es:",
                        "Fr:",
                        "It:",
                        "1/2"]

URL_OPEN_FOOD_FACT = "https://fr.openfoodfacts.org/cgi/search.pl"
