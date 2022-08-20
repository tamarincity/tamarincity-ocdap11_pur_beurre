import pytest

from accounts.models import Customer


SUT = Customer


@pytest.mark.django_db
def test_str_():

    customer = SUT.objects.create(username='Toto', customer_type="CUSTOMER")
    customer.save()

    print("customer.username: ", customer.username)
    assert SUT.__str__(customer) == f"{customer.username} ({customer.customer_type})"
