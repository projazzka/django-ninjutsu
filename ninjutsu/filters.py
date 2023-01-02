from functools import wraps
from typing import Callable

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


def filtered(filter_class: Filter):
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def filtered_view(request: HttpRequest, *args, **kwargs):
            filter_schema = kwargs.pop("ninjutsu_filters")
            queryset = view_func(request, *args, **kwargs)
            # queryset = filter_schema.filter_queryset(queryset, request)
            return queryset

        filtered_view._ninja_contribute_args = [  # type: ignore
            (
                "ninjutsu_filters",
                filter_class,
                Query(...),  # no idea what this is.
            ),
        ]
        return filtered_view

    return decorator
