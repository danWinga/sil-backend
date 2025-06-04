# orders/tests/test_orders.py

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from catalog.models import Product
from orders.models import Order

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="u", email="u@example.com", password="p")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def products(db):
    return (
        Product.objects.create(name="P1", price=5),
        Product.objects.create(name="P2", price=7),
    )


def test_create_order_and_total(client, products):
    p1, p2 = products
    payload = {
        "items": [
            {"product_id": p1.id, "quantity": 2},
            {"product_id": p2.id, "quantity": 1},
        ]
    }
    resp = client.post("/api/orders/", payload, format="json")
    assert resp.status_code == 201
    data = resp.json()
    assert data["total_price"] == "17.00"


def test_list_orders(client, user):
    # create two orders
    Order.objects.create(customer=user)
    Order.objects.create(customer=user)
    resp = client.get("/api/orders/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
