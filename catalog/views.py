# catalog/views.py

from django.db.models import Avg
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    list | retrieve | create | update | destroy
    + GET /api/categories/{id}/average_price/
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=["get"], url_path="average_price")
    def average_price(self, request, pk=None):
        cat = self.get_object()
        descendants = cat.get_descendants(include_self=True)
        result = Product.objects.filter(categories__in=descendants).aggregate(
            avg_price=Avg("price")
        )
        avg = result["avg_price"] or 0
        return Response({"category": cat.id, "average_price": float(round(avg, 2))})


class ProductViewSet(viewsets.ModelViewSet):
    """
    POST /api/products/ accepts single object or list→bulk-create.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()
        data = (
            self.get_serializer(instances, many=many).data
            if many
            else self.get_serializer(instances).data
        )
        return Response(data, status=status.HTTP_201_CREATED)
