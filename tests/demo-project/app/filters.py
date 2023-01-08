from ninjutsu import Filter


class SkuFilter(Filter):
    sku: str


class SkuStartWith(Filter):
    sku_filter: str

    class Config:
        fields = {"sku__startswith": "sku"}
