# config/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalog.views   import ProductViewSet, CategoryViewSet
from orders.views    import OrderViewSet

router = DefaultRouter()
router.register('products',  ProductViewSet,  basename='product')
router.register('categories',CategoryViewSet, basename='category')
router.register('orders',    OrderViewSet,    basename='order')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/',   include(router.urls)),
]