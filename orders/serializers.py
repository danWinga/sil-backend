# orders/serializers.py
from decimal import Decimal

from rest_framework import serializers

from catalog.models import Product

from .models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ("id", "items", "status", "total_price", "created_at")
        read_only_fields = ("id", "status", "total_price", "created_at")

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        from django.db import transaction

        with transaction.atomic():
            order = Order.objects.create(customer=user)
            for item in items_data:
                prod = Product.objects.get(pk=item["product_id"])
                # OrderItem.save() will snapshot price & compute line_price
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=item["quantity"],
                    unit_price=prod.price,
                )
            # recalc total & save
            order.total_price = order.recalc_total()
            order.save()
        return order


class OrderReadSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    customer = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ("id", "customer", "status", "total_price", "created_at", "items")

    def get_items(self, obj):
        return [
            {
                "product": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "line_price": item.line_price,
            }
            for item in obj.items.all()
        ]
