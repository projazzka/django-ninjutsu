from enum import Enum
from functools import wraps
from typing import Callable, List, Type

from django.db.models import Model, QuerySet
from django.http import Http404, HttpRequest
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Query, Router, Schema
from ninja.pagination import paginate

from .filters import Filter


class Action(Enum):
    LIST = "list"
    RETRIEVE = "retrieve"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class CrudView:
    schema: Type[Schema] | None = None
    list_schema: Type[Schema] | None = None
    retrieve_schema: Type[Schema] | None = None
    create_schema: Type[Schema] | None = None
    update_schema: Type[Schema] | None = None
    model: Type[Model] | None = None
    queryset: QuerySet | None = None
    filter_class: Type[Filter] | None = None

    def __init__(self, request: HttpRequest, action: Action):
        self.request = request
        self.action = action

    def get_queryset(self):
        return (
            self.queryset.all()  # .all() forces queryset re-evaluation!
            if self.queryset is not None
            else self.model.objects.all()
        )

    def get_model(self):
        return self.model or self.queryset.model

    def list(self):
        return self.get_queryset()

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    def retrieve(self, pk: int):
        return self.get_object(pk)

    def create(self, data: Schema):
        new = self.get_model().objects.create(**data.dict())
        return 201, new

    def update(self, pk: int, data: Schema):
        obj = self.get_object(pk)
        for key, value in data.dict().items():
            obj[key] = value
        obj.save()
        return obj

    def delete(self, pk):
        num_deleted, dummy = self.get_model().objects.filter(pk=pk).delete()
        if num_deleted:
            return 204, None
        else:
            raise Http404()


class CrudRouter(Router):
    def create_dispatcher(self, view_class: Type[CrudView]):
        create_schema = view_class.create_schema or view_class.schema
        update_schema = (
            view_class.update_schema or view_class.create_schema or view_class.schema
        )

        class CrudDispatcher:
            @classmethod
            def list(cls, request, *args, **kwargs):
                view = view_class(request, Action.LIST)
                result = view.list()
                if (
                    view.filter_class
                    and type(result) is QuerySet
                    and "ninjutsu_filter" in kwargs
                ):
                    schema = kwargs.pop("ninjutsu_filter")
                    result = schema.filter(result, request)
                return result

            @classmethod
            def retrieve(cls, request, pk: int):
                view = view_class(request, Action.RETRIEVE)
                return view.retrieve(pk)

            @classmethod
            def create(cls, request: HttpRequest, data: create_schema):  # type: ignore
                view = view_class(request, Action.CREATE)
                return view.create(data)

            @classmethod
            def update(cls, request, pk: int, data: update_schema):  # type: ignore
                view = view_class(request, Action.UPDATE)
                return view.update(pk, data)

            @classmethod
            def delete(cls, request, pk: int):
                view = view_class(request, Action.DELETE)
                return view.delete(pk)

        if view_class.filter_class:
            CrudDispatcher.list.__func__._ninja_contribute_args = [  # type: ignore
                (
                    "ninjutsu_filter",
                    view_class.filter_class,
                    Query(...),  # no idea what this is.
                ),
            ]
        return CrudDispatcher

    def register(self, sub_path: str, view_class: Type[CrudView]) -> Type[CrudView]:
        dispatcher = self.create_dispatcher(view_class)
        list_schema = view_class.list_schema or view_class.schema
        retrieve_schema = view_class.retrieve_schema or view_class.schema

        self.add_api_operation(
            f"{sub_path}/",
            ["GET"],
            dispatcher.list,
            response=List[list_schema],  # type: ignore
        )
        self.add_api_operation(
            f"{sub_path}/{{pk}}",
            ["GET"],
            dispatcher.retrieve,
            response=retrieve_schema,
        )
        self.add_api_operation(
            f"{sub_path}/",
            ["POST"],
            dispatcher.create,
            response={201: retrieve_schema},
        )
        self.add_api_operation(
            f"{sub_path}/{{pk}}", ["PUT"], dispatcher.update, response=retrieve_schema
        )
        self.add_api_operation(
            f"{sub_path}/{{pk}}",
            ["DELETE"],
            dispatcher.delete,
            response={204: None, 404: None},
        )
        return view_class

    def path(self, sub_path: str) -> Callable[[Type[CrudView]], Type[CrudView]]:
        def inner(view: Type[CrudView]) -> Type[CrudView]:
            self.register(sub_path, view)
            return view

        return inner
