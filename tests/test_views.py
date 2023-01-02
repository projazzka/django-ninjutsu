import pytest
from app.models import Product
from django.test import Client


@pytest.fixture
def single_object():
    obj = Product.objects.create(
        sku="PROD001",
        price="12.34",
    )
    return obj


def test_single_receive(db, client, single_object):
    response = client.get(f"/api/products/{single_object.pk}")

    data = response.json()
    assert data["sku"] == "PROD001"
    assert data["price"] == "12.34"
    assert data["stock"] == 0
    assert not (set(data.keys()).difference({"id", "sku", "price", "stock"}))


def test_single_list(db, client, single_object):
    response = client.get("/api/products/")

    items = response.json()
    assert len(items) == 1
    data = items[0]
    assert data["sku"] == "PROD001"
    assert data["price"] == "12.34"
    assert data["stock"] == 0
    assert not (set(data.keys()).difference({"id", "sku", "price", "stock"}))


def test_create(db, client: Client):
    response = client.post(
        "/api/products/",
        {
            "sku": "PROD002",
            "price": "23.45",
            "stock": 10,
        },
        content_type="application/json",
    )
    print(response.content)
    assert response.status_code == 201

    data = response.json()
    assert data["sku"] == "PROD002"
    assert data["price"] == "23.45"
    assert data["stock"] == 10
    assert not (set(data.keys()).difference({"id", "sku", "price", "stock"}))


def test_single_delete(db, client: Client, single_object):
    response = client.delete(f"/api/products/{single_object.pk}")

    assert response.status_code == 204
    assert not response.content


def test_single_delete_not_found(db, client: Client, single_object):
    response = client.delete(f"/api/products/{single_object.pk + 1}")

    assert response.status_code == 404
