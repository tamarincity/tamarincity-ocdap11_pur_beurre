from django.db import models
from django.contrib.auth.models import AbstractUser


class Customer(AbstractUser):
    class CustomerType(models.TextChoices):
        CUSTOMER = "Client"
        PREMIUM_CUSTOMER = "Client Premium"
        VIP = "VIP"

    customer_type = models.CharField(
        choices=CustomerType.choices, default=CustomerType.CUSTOMER, max_length=30)

    def __str__(self):
        return f"{self.username} ({self.customer_type})"
