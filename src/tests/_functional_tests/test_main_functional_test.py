import time

import pytest

from accounts.constants import USER_LARA_CROFT


@pytest.mark.functional_test
@pytest.mark.usefixtures("init_driver")  # From conftest.py - Select and initialyze the driver
class TestApplication:
    def test_signup(self):
        try:
            driver = self.driver
            find = driver.find_element_by_xpath

            # Remove fake users from database
            driver.get("http://142.93.142.2/accounts_delete_fake_users")

            # Go to home page
            print("No characters after the domain name should take the user to the home page")
            driver.get("http://142.93.142.2")
            time.sleep(2)
            h1_content = find("//h1").text
            assert "Du gras, oui, mais de qualit" in h1_content

            # Enter keywords to get the original product
            print("Entering keywords in the search bar")
            field_enter_product_keywords = find("//input[@id='form1']")
            field_enter_product_keywords.send_keys("coca cola")
            # Click submit
            find("//button[@type='submit']").click()
            time.sleep(2)

            print("     should take the user to the original products page even though the "
                    "user is not logged in")
            assert ("Choisissez dans la liste ci-dessous le produit que vous voulez remplacer."
                    in driver.page_source)

            print("     so that he can select the product he wants to substitute "
                    "among a list of products")
            selected_product = find('//div[contains(text(), "original")]')
            assert selected_product

            # Click on the original product to get the substitute products list
            print("Clicking on the original product")
            selected_product.click()
            time.sleep(2)

            print("     should take the user to the substitute products page")
            assert "Vous pouvez remplacer cet aliment par" in driver.page_source

            # Click on substitute product to get details
            print("Clicking on a substitute product", end=" ")
            selected_product = find("//button[@class='product-as-button']")
            selected_product.click()
            time.sleep(2)

            print("should take the user to the details page of the substitute product")
            assert "nutritionnels pour 100g" in driver.page_source

            # Click on button to go to the OpenFoodFact web site to get more information
            print("Clicking the button <<Voir la fiche d'OpenFoodFact>>")
            openfoodfact_btn = find("//button[@class='biscuits-as-background-for-button']")
            openfoodfact_btn.click()
            time.sleep(5)

            print("     should take the user to the details page of the substitute product "
                    "on https://fr.openfoodfacts.org/ (in a new tab)")
            driver.switch_to.window(driver.window_handles[1])  # Switch to new window
            assert "Open Food Facts" in driver.page_source
            assert "les produits alimentaires du monde entier." in driver.page_source
            time.sleep(2)

            # Close the OpenFoodFact page
            print("Closing the new tab should take back the user to the Pure Beurre application")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])  # Switch to previous window

            # Go to sign up page
            print("When << s'inscrire >> is clicked should take the user to "
                    "signup page")
            # Click on sign up link
            find("//a[contains(@href,'/accounts_signup')]").click()
            time.sleep(2)
            h2_content = find("//h2").text
            assert "inscrire" in h2_content

            # Fill in the signup form
            print("If the signup form is properly filled and submitted then")
            email_field = find('//*[@id="username"]')
            email_field.send_keys(USER_LARA_CROFT["username"])
            password_field = find('//*[@id="password"]')
            password_field.send_keys(USER_LARA_CROFT["password"])
            # Click on the submit button
            find('//*[@id="submitButton"]').click()
            time.sleep(2)

            print("     should redirect the user to home page")
            h1_content = find("//h1").text
            assert "Du gras, oui, mais de qualit" in h1_content

            print("     should connect the user. As a result, the logout "
                    "button is displayed")
            link_to_logout = driver.find_element_by_xpath('//a[@id="logout"]')
            assert link_to_logout

            # Enter keywords to get the original product
            print("Entering keywords in the search bar")
            field_enter_product_keywords = find("//input[@id='form1']")
            field_enter_product_keywords.send_keys("coca cola")
            # Click submit
            find("//button[@type='submit']").click()
            time.sleep(2)

            print("     should take the user to the original products page")
            assert ("Choisissez dans la liste ci-dessous le produit que vous voulez remplacer."
                    in driver.page_source)

            print("     so that he can select the product he wants to substitute "
                    "among a list of products")
            selected_product = find('//div[contains(text(), "original")]')
            assert selected_product

            # Click on the original product to get the substitute products list
            print("Clicking on the original product")
            selected_product.click()
            time.sleep(2)

            print("     should take the user to the substitute products page")
            assert "Vous pouvez remplacer cet aliment par" in driver.page_source

            # Click on button to add the substitute product to the favorite food list
            print("Clicking on the button 'Ajouter à mes aliments'", end=" ")
            add_to_fav_btn = find("//*[contains(text(), 'Ajouter')]")
            add_to_fav_btn.click()
            time.sleep(2)

            print("should display the message: "
                    "Ce produit a bien été enregistré dans vos aliments préférés.")
            assert "Ce produit a bien " in driver.page_source
            assert "enregistr" in driver.page_source
            assert " dans vos aliments pr" in driver.page_source

            # Click on button to go to the favorites page
            print("Clicking on 'mes aliments' (the carrot icon)")
            favorites_link = find("//a[@id='get_fav']")
            favorites_link.click()
            time.sleep(2)

            print("     should take the user to the favorites page")
            assert "Mes aliments" in driver.page_source

            print("     should display the favorites products")
            image_of_product = find("//img[@class='image-thumb-of-product']")
            assert image_of_product

            # Click on icon to logout
            print("Clicking on the 'logout' icon ")
            logout_link = find("//a[@id='logout']")
            logout_link.click()
            time.sleep(2)

            print("     should redirect the user to home page")
            h1_content = find("//h1").text
            assert "Du gras, oui, mais de qualit" in h1_content

            print("     should log-out the user from the app. As a result, "
                    "the login link is displayed")
            assert "inscrire" in driver.page_source

            time.sleep(2)
            # Remove fake users from database
            driver.get("http://142.93.142.2/accounts_delete_fake_users")

        except Exception as e:
            driver.save_screenshot("screenshot_of fail.png")
            print("TEST FAILED! Reason: ", str(e))
            if "connection" in str(e).lower():
                assert "Functional test failed! Maybe the server is not running." in str(e)
            else:
                assert "Functional test failed!" in ""
