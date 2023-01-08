from ninja import ModelSchema

from .models import Product


class ProductSchema(ModelSchema):
    class Config:
        model = Product
        model_fields = "sku price stock".split()


class ShortProductSchema(ModelSchema):
    class Config:
        model = Product
        model_fields = "sku price".split()


class DetailedProductSchema(ModelSchema):
    class Config:
        model = Product
        model_fields = "__all__"
