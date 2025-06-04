# notifications/tests/test_notifications.py

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from catalog.models import Product
from notifications.tasks import send_order_notification
from orders.models import Order, OrderItem

User = get_user_model()


@pytest.fixture
def order(db):
    # Create a user, product, order and orderitem with Decimal prices
    user = User.objects.create_user("u", "u@example.com", "p")
    p = Product.objects.create(name="X", price=Decimal("9.00"))
    order = Order.objects.create(customer=user)
    OrderItem.objects.create(
        order=order, product=p, quantity=1, unit_price=Decimal("9.00")
    )
    return order


def test_notification_task_runs_without_exception(monkeypatch, order):
    """
    Ensure the Celery task runs without error, stubbing out external SMS/email.
    """
    # Stub Africa's Talking initialization & SMS.send
    monkeypatch.setattr("africastalking.initialize", lambda **kw: None)

    class SMSStub:
        @staticmethod
        def send(message, recipients):
            # do nothing
            return {"status": "sent"}

    monkeypatch.setattr("africastalking.SMS", SMSStub)

    # Stub Django send_mail
    monkeypatch.setattr("django.core.mail.send_mail", lambda **kw: 1)

    # Call the task synchronously
    send_order_notification(order.id)
    # No exception => pass
