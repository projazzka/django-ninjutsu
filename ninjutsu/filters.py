from functools import wraps
from typing import Callable, List, Type

from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Query, Schema
from pydantic.fields import ModelField

CUSTOM_FILTER_PREFIX = "filter_"


class Filter(Schema):
    def filter(self, queryset: QuerySet, request: HttpRequest):
        custom_filters = [
            attr[len(CUSTOM_FILTER_PREFIX) :]
            for attr in dir(self)
            if attr.startswith(CUSTOM_FILTER_PREFIX)
        ]
        filter_values = {
            key: value
            for (key, value) in self.dict().items()
            if value and key not in custom_filters
        }
        queryset = queryset.filter(**filter_values)
        for name in custom_filters:
            custom_filter = getattr(self, f"{CUSTOM_FILTER_PREFIX}{name}")
            value = getattr(self, name)
            queryset = custom_filter(queryset, name=name, value=value)
        return queryset


def apply_filters(
    queryset: QuerySet, request: HttpRequest, filters: List[Type[Filter]]
) -> QuerySet:
    for filter_class in filters:
        instance = filter_class(**request.GET)
        queryset = instance.filter(queryset, request)
    return queryset
