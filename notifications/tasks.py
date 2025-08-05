# notifications/tasks.py

import logging

import africastalking
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from orders.models import Order

logger = logging.getLogger(__name__)


def send_order_notification(order_id):
    """
    Synchronous helper for tests.
    """
    order = (
        Order.objects.select_related("customer")
        .prefetch_related("items__product")
        .get(pk=order_id)
    )
    cust = order.customer
    phone = (getattr(cust, "phone_number", "") or "").strip()

    # 1) SMS
    if settings.AFRICAS_TALKING_USERNAME and settings.AFRICAS_TALKING_API_KEY and phone:
        africastalking.initialize(
            username=settings.AFRICAS_TALKING_USERNAME,
            api_key=settings.AFRICAS_TALKING_API_KEY,
        )
        # Add senderId here if it's needed for synchronous testing
        sms_params = {
            "message": f"Your order #{order.id} is confirmed (KES {order.total_price})",
            "recipients": [phone],
        }
        if settings.AFRICAS_TALKING_SENDER_ID:
            sms_params["senderId"] = settings.AFRICAS_TALKING_SENDER_ID
        africastalking.SMS.send(**sms_params)


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

    # Log the phone number for debugging
    logger.info(f"Attempting to send SMS for order {order_id} to {phone}")

    try:
        africastalking.initialize(
            username=settings.AFRICAS_TALKING_USERNAME,
            api_key=settings.AFRICAS_TALKING_API_KEY,
        )

        # Prepare parameters for the SMS.send() method
        sms_params = {
            "message": f"Hi {order.customer.username}, your order #{order.id} "
                       f"for KES {order.total_price} is confirmed.",
            "recipients": [phone],
        }

        # Dynamically add senderId if it's available in settings
        if settings.AFRICAS_TALKING_SENDER_ID:
            sms_params["senderId"] = settings.AFRICAS_TALKING_SENDER_ID
            logger.info(f"Using senderId: {settings.AFRICAS_TALKING_SENDER_ID}") # Log senderId used

        # Pass the parameters using ** to unpack the dictionary
        resp = africastalking.SMS.send(**sms_params)
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
    order = (
        Order.objects.select_related("customer")
        .prefetch_related("items__product")
        .get(pk=order_id)
    )

    items_str = "\n".join(
        f"{i.quantity}×{i.product.name} = {i.line_price}" for i in order.items.all()
    )
    subject = f"New Order #{order.id} Placed"
    body = (
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