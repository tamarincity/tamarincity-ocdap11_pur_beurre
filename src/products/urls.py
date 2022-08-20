from django.urls import path

from products import views

urlpatterns = [
    # Home page
    path('home', views.home, name='products_home'),
    # Route to store the original product and its substitute to the database
    path('add_to_favorites', views.add_to_favorites, name='products_add_to_favorites'),
    # Route for the user to send a message
    path('contact', views.contact, name='products_contact'),
    # Route to get the details of a substitute product
    path('details', views.details, name='products_details'),
    # Route for a user to get its favorite products
    path('favorites', views.get_all_favorites, name='products_favorites'),
    # Route to receive the message from the contact page
    path('get-message', views.get_message, name='products_get_message'),
    # Route to get the original product after submitting the form
    path('get-origial-product', views.get_origial_product, name='products_get_origial_product'),
    # Route to get a list of substitute products for an original product
    path('get-substitutes', views.get_substitutes, name='products_get_substitutes'),
    # Route to go to the page of the legal notice
    path('legal_notice', views.legal_notice, name='products_legal_notice'),
    # Home page
    path('', views.home, name='products_home'),
]
