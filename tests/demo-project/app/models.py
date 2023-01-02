from django.db import models


class Product(models.Model):
    sku = models.CharField(max_length=16)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
