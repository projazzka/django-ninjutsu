from ninjutsu import CrudRouter, CrudView

from .models import Product
from .schemas import ProductSchema
from .filters import SkuFilter

router = CrudRouter()


@router.path("products/")
class ProductView(CrudView):
    schema = ProductSchema
    queryset = Product.objects.all()


@router.path("by-sku/")
class BySkyView(CrudView):
    schema = ProductSchema
    queryset = Product.objects.all()
    filter_class = SkuFilter
