# orders/models.py
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.db.models import F, Sum
from django.utils import timezone


class Order(models.Model):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELED = "canceled"

    STATUS_CHOICES = [
        (NEW, "New"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (CANCELED, "Canceled"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=NEW)
    total_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def recalc_total(self):
        agg = self.items.aggregate(total=Sum(F("unit_price") * F("quantity")))[
            "total"
        ] or Decimal("0.00")
        return agg.quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        # ensure total_price matches items
        if self.pk:
            self.total_price = self.recalc_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk} by {self.customer.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = [("order", "product")]
        indexes = [
            models.Index(fields=["order"]),
        ]

    def save(self, *args, **kwargs):
        # always snapshot the product price at the time of ordering
        if not self.unit_price:
            self.unit_price = self.product.price
        self.line_price = (self.unit_price * self.quantity).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}×{self.product.name} @ {self.unit_price}"
