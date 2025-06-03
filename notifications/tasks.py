# # notifications/tasks.py
# from celery import shared_task
# from django.conf import settings
# from django.core.mail import send_mail
# from africastalking import AfricasTalking
# from orders.models import Order

# notifications/tasks.py

# from celery import shared_task
# from django.conf import settings
# from django.core.mail import send_mail
# import africastalking
# from orders.models import Order

# @shared_task
# def send_order_notification(order_id):
#     order = (
#         Order.objects
#         .select_related("customer")
#         .prefetch_related("items__product")
#         .get(pk=order_id)
#     )
#     customer = order.customer
#     items = [
#         f"{i.quantity}×{i.product.name}@{i.unit_price}"
#         for i in order.items.all()
#     ]
#     total = order.total_price

#     # 1) Initialize Africa's Talking (if creds provided)
#     if settings.AFRICAS_TALKING_USERNAME and settings.AFRICAS_TALKING_API_KEY and customer.phone_number:
#         africastalking.initialize(
#             username=settings.AFRICAS_TALKING_USERNAME,
#             api_key=settings.AFRICAS_TALKING_API_KEY,
#         )
#         sms = africastalking.SMS
#         try:
#             sms.send(
#                 message=f"Your order #{order_id} has been placed. Total: {total}",
#                 recipients=[customer.phone_number],
#             )
#         except Exception as e:
#             # log or handle SMS failure
#             print("SMS send failed:", e)

#     # 2) Send admin email
#     try:
#         send_mail(
#             subject=f"New Order #{order_id}",
#             message=(
#                 f"Customer {customer.username} placed order #{order_id}:\n"
#                 + "\n".join(items)
#                 + f"\nTotal: {total}"
#             ),
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[settings.ADMIN_EMAIL],
#             fail_silently=False,
#         )
#     except Exception as e:
#         print("Email send failed:", e)

# notifications/tasks.py

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import africastalking
from orders.models import Order
import logging


logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_sms(self, order_id):
    """
    Send SMS via Africa's Talking. Retries on network errors only.
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
        # retry only on network/API errors
        logger.error("SMS send failed for order %s: %s", order_id, exc, exc_info=True)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_email(self, order_id):
    """
    Send email to admin with order details. Retries on any failure.
    """
    import sys, os
    logger.info("send_order_email CALLED for order %s", order_id)
    print(f"send_order_email CALLED for order {order_id}", file=sys.stderr)
    print("EMAIL_HOST is", os.environ.get("EMAIL_HOST"), file=sys.stderr)
    # raise Exception("DEBUG")

    order = Order.objects.select_related("customer") \
                         .prefetch_related("items__product") \
                         .get(pk=order_id)

    items_str = "\n".join(
        f"{item.quantity}×{item.product.name} = {item.line_price}"
        for item in order.items.all()
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