from ninjutsu import CrudRouter, CrudView

from .models import Product
from .schemas import ProductSchema

router = CrudRouter()


@router.path("products/")
class ProductView(CrudView):
    schema = ProductSchema
    queryset = Product.objects.all()
