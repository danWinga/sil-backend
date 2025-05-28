# # notifications/tasks.py
# from celery import shared_task
# from django.conf import settings
# from django.core.mail import send_mail
# from africastalking import AfricasTalking
# from orders.models import Order

# @shared_task
# def send_order_notification(order_id):
#     order = Order.objects.prefetch_related('items', 'customer').get(pk=order_id)
#     phone = order.customer.phone_number
#     email = order.customer.email
#     items = [
#         f"{it.quantity}×{it.product.name}@{it.unit_price}"
#         for it in order.items.all()
#     ]
#     total = order.total_price

#     # SMS
#     at = AfricasTalking(
#         username=settings.AFRICAS_TALKING_USERNAME,
#         api_key=settings.AFRICAS_TALKING_API_KEY,
#     )
#     sms = at.SMS
#     sms.send(
#         message=f"Your order #{order_id} has been placed. Total: {total}",
#         recipients=[phone],
#     )

#     # Email to ADMIN_EMAIL
#     send_mail(
#         subject=f"New Order #{order_id}",
#         message=f"Customer {order.customer.username} ordered:\n" +
#                 "\n".join(items) +
#                 f"\nTotal: {total}",
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[settings.ADMIN_EMAIL],
#         fail_silently=False,
#     )

# notifications/tasks.py

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
import africastalking
from orders.models import Order

@shared_task
def send_order_notification(order_id):
    order = (
        Order.objects
        .select_related("customer")
        .prefetch_related("items__product")
        .get(pk=order_id)
    )
    customer = order.customer
    items = [
        f"{i.quantity}×{i.product.name}@{i.unit_price}"
        for i in order.items.all()
    ]
    total = order.total_price

    # 1) Initialize Africa's Talking (if creds provided)
    if settings.AFRICAS_TALKING_USERNAME and settings.AFRICAS_TALKING_API_KEY and customer.phone_number:
        africastalking.initialize(
            username=settings.AFRICAS_TALKING_USERNAME,
            api_key=settings.AFRICAS_TALKING_API_KEY,
        )
        sms = africastalking.SMS
        try:
            sms.send(
                message=f"Your order #{order_id} has been placed. Total: {total}",
                recipients=[customer.phone_number],
            )
        except Exception as e:
            # log or handle SMS failure
            print("SMS send failed:", e)

    # 2) Send admin email
    try:
        send_mail(
            subject=f"New Order #{order_id}",
            message=(
                f"Customer {customer.username} placed order #{order_id}:\n"
                + "\n".join(items)
                + f"\nTotal: {total}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
    except Exception as e:
        print("Email send failed:", e)