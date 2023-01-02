# django-ninjutsu

django-ninjutsu gives you simple class-based CRUD views on top of vitalik's fancy REST-API framework for Django called django-ninja.
In very much the same spirit, django-ninjutsu introduces filter schemas in order to represent filtering parameters.
Just like in django-ninja input and output serializers ("schemas") are expressed in a very pythonic way as pydantic models.

> :warning: This package is not production ready. It is currently more of a proof of concept. Currently asynchronous views are not considered.

## Installation

pip install django-ninjutsu


## Usage

As an example consider the following model:

```Python
def Product(models.Model):
    sku = models.CharField(max_length=16)
    price = models.DecimalField(max_digits=6, decimals=2)
    on_sale = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
```

In urls.py, where you normally would instantiate your NinjaAPI,

```Python
from ninjutsu import CrudView, CrudRouter

from .models import Product


class ProductSchema(ModelSchema):
    class Config:
        model = Product
        fields = ['__all__',]


router = CrudRouter()

@router.path("products/")
class ProductView(CrudView):
    schema = ProductSchema
    queryset = Product.objects.all()
```

That's it. This automatically adds the following endpoints to your API:

  * GET /products/  (lists all objects)
  * POST /products/  (creates a new object)
  * GET /products/{id}  (retrieves a single object)
  * PUT /products/{id}  (updates an object)
  * DELETE /products/{id} (deletes an object)

These are ready-to-use. Together with filtering and authorization (explained below) might be actually enough for your application, without any view-related code.


## Filtering

Very much in the spirit of djangon-ninja, filter definitions in django-ninjutsu are expressed as pydantic models. A filter class defines the query params that can be applied as django filter arguments to the resulting queryset.

Example: 

```Python
from ninjutsu import Filter


class OrderFilter(Filter):
    price : decimal | None
    sku: str | None


@router.path("products/")
class ProductView(CrudView):
    schema = ProductSchema
    filters = [ProductFilter, ]
    queryset = Product.objects.all()

```

/products/?sku=PROD001
queryset = queryset.filter(sku='PROD001')


### Filter fields with aliases

Standard pydantic aliases transform query params into other

```Python
class SinceFilter(Filter):
    since : datetime

    class Config:
        fields = {"since": "date__gte"}
```

A call to 
`/products/?since=2020-01-01`
filters the result like
queryset = queryset.filter(date__gte=datetime.datetime(2020, 1, 1))


### Custom filters

For each filter field you can define a custom filter function following the naming convention of the prefix "filter_" plus the field name.

```Python
class ExcludeShirts(Filter):
    no_shirts: bool = False
    
    def filter_no_shirts(self, queryset, value):
        if value:
            queryset = queryset.exclude(sku__startswith='SHIRT')
        return queryset
```

If you need full control you can even override the `filter` function that handels filtering for all fields.


## Schema selection

Sometimes it comes in handy to be able to specify a specific different schema for one or more actions. E.g. you might want to expose less fields in the list endpoint.

```Python
class ProductListSchema(ProductSchema):
    class Config(ProductSchema.Config):
        fields = ['sku', 'price',]


@router.path("products/")
class ProductView(CrudView):
    schema = ProductSchema
    schema_list = ProductListSchema
    queryset = Product.objects.all()
```

You can specify more specific schemata for all five actions (create, retrieve, update, delete and list). If they are not specified the view falls back to `schema`.


### Dynamic schema selection

For situations in which you need more control, e.g. if you want to take into account user permissions etc., you can also override the `get_schema` function.

```Python
class ProductView(CrudView):
    schema = ProductSchema

    def get_schema(self):
        if self.action == 'list' and not self.request.user.is_staff():
            return PruductListSchema
        else
            return ProductSchema
```

Note that `get_schema` can use internal properties `action` and `request`.


## Authorization

While django-ninja already handles authentication, django-ninjutsu permissions helps you to decide whether the authenticated client has access to certain contents.

```Python
class AuthenticatedOrFree(BasePermission):
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        return False
```

