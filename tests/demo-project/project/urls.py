from app.api import router as app_router
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

api = NinjaAPI()
api.add_router("", app_router)


urlpatterns = [
    path("api/", api.urls),
    path("admin/", admin.site.urls),
]
