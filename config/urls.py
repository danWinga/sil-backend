# config/urls.py

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalog.views import CategoryViewSet, ProductViewSet
from orders.views import OrderViewSet

from drf_spectacular.views import (
  SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
)

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]


urlpatterns += [
  path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
  path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
  path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
