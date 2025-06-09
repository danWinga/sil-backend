# config/urls.py

from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalog.views import CategoryViewSet, ProductViewSet
from orders.views import OrderViewSet

from drf_spectacular.views import (
  SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
)
from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")
router.register("orders", OrderViewSet, basename="order")

# wrap docs views with AllowAny so they’re public
schema_view = SpectacularAPIView.as_view(permission_classes=[AllowAny])
swagger_view = SpectacularSwaggerView.as_view(
    url_name="schema", permission_classes=[AllowAny]
)
redoc_view = SpectacularRedocView.as_view(
    url_name="schema", permission_classes=[AllowAny]
)

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("api/", include(router.urls)),
# ]


# urlpatterns += [
#   path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
#   path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
#   path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
# ]

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API endpoints (protected by OIDC or BasicAuth in DEBUG)
    path("api/", include(router.urls)),
    path("api/schema/", include(router.urls),schema_view, name="schema"),

    # OpenAPI schema and documentation (public)
    path("api/schema/", schema_view, name="schema"),
    path("api/docs/", swagger_view, name="swagger-ui"),
    path("api/redoc/", redoc_view, name="redoc"),
]
