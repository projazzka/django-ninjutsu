from decimal import Decimal
from typing import List
import pytest
from app.models import Product
from django.test import Client


pytestmark = pytest.mark.usefixtures("db")


@pytest.fixture
def single_object():
    obj = Product.objects.create(
        sku="PROD001",
        price="12.34",
    )
    return obj


@pytest.fixture
def three_objects():
    return [
        Product.objects.create(sku=sku, price=price, stock=stock)
        for (sku, price, stock) in [
            ("SHIRT001", "12.5", 10),
            ("SHIRT002", "13.5", 15),
            ("CAPPIE01", "4.95", 50),
        ]
    ]


def test_single_receive(client, single_object):
    response = client.get(f"/api/products/{single_object.pk}")

    data = response.json()
    assert data["sku"] == "PROD001"
    assert data["price"] == "12.34"
    assert data["stock"] == 0
    assert not (set(data.keys()).difference({"id", "sku", "price", "stock"}))


def test_single_list(client, single_object):
    response = client.get("/api/products/")

    items = response.json()
    assert len(items) == 1
    data = items[0]
    assert data["sku"] == "PROD001"
    assert data["price"] == "12.34"
    assert data["stock"] == 0
    assert not (set(data.keys()).difference({"id", "sku", "price", "stock"}))


def test_create(client: Client):
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


def test_single_delete(client: Client, single_object):
    response = client.delete(f"/api/products/{single_object.pk}")

    assert response.status_code == 204
    assert not response.content


def test_single_delete_not_found(client: Client, three_objects: List[Product]):
    response = client.delete(f"/api/products/123")

    assert response.status_code == 404


def test_empty_list(client):
    response = client.get("/api/products/")

    items = response.json()
    assert type(items) is list
    assert len(items) == 0


def test_retrieve_not_found(client, three_objects):
    response = client.get("/api/products/123")

    assert response.status_code == 404


def test_filter_by_sku(client: Client, three_objects):
    response = client.get("/api/by-sku/?sku=SHIRT002")

    assert response.status_code == 200
    items = response.json()
    assert type(items) is list
    assert len(items) == 1
    item = items[0]
    assert item["sku"] == "SHIRT002"
    assert Decimal(item["price"]) == Decimal("13.5")
    assert item["stock"] == 15
