# notifications/tasks.py

import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import africastalking
from orders.models import Order

logger = logging.getLogger(__name__)

def send_order_notification(order_id):
    """
    Synchronous helper for tests.
    """
    order = (Order.objects
                 .select_related("customer")
                 .prefetch_related("items__product")
                 .get(pk=order_id))
    cust  = order.customer
    phone = (getattr(cust, "phone_number", "") or "").strip()

    # 1) SMS
    if settings.AFRICAS_TALKING_USERNAME and settings.AFRICAS_TALKING_API_KEY and phone:
        africastalking.initialize(
            username=settings.AFRICAS_TALKING_USERNAME,
            api_key=settings.AFRICAS_TALKING_API_KEY,
        )
        africastalking.SMS.send(
            message=f"Your order #{order.id} is confirmed (KES {order.total_price})",
            recipients=[phone],
        )

    # 2) Email
    items_list = "\n".join(
        f"{item.quantity}×{item.product.name} = {item.line_price}"
        for item in order.items.all()
    )
    body = (
        f"Customer: {cust.email}\n"
        f"Total: KES {order.total_price}\n\n"
        f"Items:\n{items_list}"
    )
    send_mail(
        subject=f"New Order #{order.id}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_sms(self, order_id):
    """
    Async SMS task via Africa's Talking.
    """
    order = Order.objects.select_related("customer").get(pk=order_id)
    phone = (order.customer.phone_number or "").strip()
    if not phone:
        logger.warning("No phone for order %s – skipping SMS", order_id)
        return

    try:
        africastalking.initialize(
            username=settings.AFRICAS_TALKING_USERNAME,
            api_key=settings.AFRICAS_TALKING_API_KEY,
        )
        resp = africastalking.SMS.send(
            message=f"Hi {order.customer.username}, your order #{order.id} "
                    f"for KES {order.total_price} is confirmed.",
            recipients=[phone],
        )
        logger.info("SMS sent for order %s: %s", order_id, resp)
    except Exception as exc:
        logger.error("SMS send failed for order %s: %s", order_id, exc, exc_info=True)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_email(self, order_id):
    """
    Async email task to admin.
    """
    logger.info("send_order_email CALLED for order %s", order_id)
    order = (Order.objects
                 .select_related("customer")
                 .prefetch_related("items__product")
                 .get(pk=order_id))

    items_str = "\n".join(
        f"{i.quantity}×{i.product.name} = {i.line_price}"
        for i in order.items.all()
    )
    subject = f"New Order #{order.id} Placed"
    body    = (
        f"Customer: {order.customer.email}\n"
        f"Total: KES {order.total_price}\n\n"
        f"Items:\n{items_str}"
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        logger.info("Admin email sent for order %s", order_id)
    except Exception as exc:
        logger.error("Email send failed for order %s: %s", order_id, exc, exc_info=True)
        raise self.retry(exc=exc)