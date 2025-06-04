# orders/views.py

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from notifications.tasks import send_order_email, send_order_sms

from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer


class OrderViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """
    POST /api/orders/ → creates an order + fires async SMS+email.
    GET  /api/orders/ → list the authenticated user's orders.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderReadSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        # fire off both notifications
        send_order_sms.delay(order.id)
        send_order_email.delay(order.id)
