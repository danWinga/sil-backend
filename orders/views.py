# orders/views.py

# from rest_framework import mixins, viewsets
# from rest_framework.permissions import IsAuthenticated
# from notifications.tasks import send_order_notification
# from .models import Order
# from .serializers import OrderCreateSerializer, OrderReadSerializer

# class OrderViewSet(
#     mixins.CreateModelMixin,
#     mixins.ListModelMixin,
#     viewsets.GenericViewSet
# ):
#     """
#     Creates orders (POST /api/orders/) and lists a user's orders (GET /api/orders/).
#     Fires a Celery notification task on create.
#     """
#     permission_classes = [IsAuthenticated]

#     # Required by DRF for the ListModelMixin
#     queryset = Order.objects.none()

#     def get_queryset(self):
#         # Only return the authenticated user's orders
#         return Order.objects.filter(customer=self.request.user)

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return OrderCreateSerializer
#         return OrderReadSerializer

#     def perform_create(self, serializer):
#         order = serializer.save()
#         # fire-and-forget async notification
#         send_order_notification.delay(order.id)


# orders/views.py

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from notifications.tasks import send_order_sms, send_order_email
from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer

class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        return (
            OrderCreateSerializer if self.action == "create"
            else OrderReadSerializer
        )

    def perform_create(self, serializer):
        order = serializer.save()
        # fire off both notifications independently
        send_order_sms.delay(order.id)
        send_order_email.delay(order.id)