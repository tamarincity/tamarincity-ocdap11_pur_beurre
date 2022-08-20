from django.urls import path

from accounts import views

urlpatterns = [
    # route for the user to get his account info
    path('account', views.account, name='accounts_account'),
    # route to remove fake users from database
    path('delete_fake_users', views.delete_fake_users, name='delete_fake_users'),
    # route for the user to log in
    path('login', views.login_user, name='accounts_login'),
    # route for the user to log out
    path('logout', views.logout_user, name='accounts_logout'),
    # route for the user to sign up
    path('signup', views.signup_user, name='accounts_signup'),
]
