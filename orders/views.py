# orders/views.py
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from notifications.tasks import send_order_notification
from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer

class OrderViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderReadSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        # fire-and-forget async notification
        send_order_notification.delay(order.id)