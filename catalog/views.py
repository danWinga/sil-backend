# catalog/views.py

from django.db.models import Avg
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """
    Now supports list, retrieve, create, update, destroy
    plus our custom average_price action.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=['get'], url_path='average_price')
    def average_price(self, request, pk=None):
        cat = self.get_object()
        cats = cat.get_descendants(include_self=True)
        avg = Product.objects.filter(categories__in=cats) \
                             .aggregate(average_price=Avg('price'))['average_price'] or 0
        return Response({
            'category': cat.id,
            'average_price': round(avg, 2)
        })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        """
        Bulk upload: accept a list of product objects.
        """
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)