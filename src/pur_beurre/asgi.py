"""
ASGI config for pur_beurre project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

import environ

from django.contrib.auth.models import User


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pur_beurre.settings')

application = get_asgi_application()

# =================================================================
# Automatically creating super user

env = environ.Env(DEBUG=(bool, False))

users = User.objects.all()

if not users:
    User.objects.create_superuser(
        username=env('DJANGO_SUPERUSER_USERNAME'),
        email=env('DJANGO_SUPERUSER_EMAIL'),
        password=env('DJANGO_SUPERUSER_PASSWORD'),
        is_active=True,
        is_staff=True)
