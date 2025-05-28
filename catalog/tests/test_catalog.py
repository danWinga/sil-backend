import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from catalog.models import Category, Product

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
def category(db):
    return Category.objects.create(name="Cat", slug="cat")

def test_bulk_upload_products(client, category):
    payload = [
      {"name":"A","description":"","price":"1.00","categories":[category.id]},
      {"name":"B","description":"","price":"2.00","categories":[category.id]},
    ]
    resp = client.post("/api/products/", payload, format="json")
    assert resp.status_code == 201
    assert Product.objects.count() == 2

def test_average_price_endpoint(client, category):
    p1 = Product.objects.create(name="P1", price=10); p1.categories.add(category)
    p2 = Product.objects.create(name="P2", price=30); p2.categories.add(category)
    resp = client.get(f"/api/categories/{category.id}/average_price/")
    assert resp.status_code == 200
    assert resp.json()["average_price"] == 20.0