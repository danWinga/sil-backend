#!/usr/bin/env python
import os, json, logging, pika, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","config.settings")
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from africastalking import AfricasTalking

log = logging.getLogger(__name__)

# Init SMS
AT = AfricasTalking(username=settings.AFRICAS_TALKING_USERNAME,
                   api_key=settings.AFRICAS_TALKING_API_KEY).SMS

EXCHANGE  = "si.orders"
QUEUE     = "si.notifications"

def handle(ch, method, props, body):
    data = json.loads(body)
    log.info(f"Processing order.created: {data}")

    # Send SMS
    try:
        if data.get("customer_phone"):
            AT.send(message=f"Order #{data['order_id']} confirmed. Total KES {data['total_price']}.",
                    recipients=[data["customer_phone"]])
    except Exception:
        log.exception("SMS failed")

    # Send email to admin
    try:
        items = "\n".join(f"{i['quantity']}×{i['name']} = {i['line_price']}" for i in data["items"])
        send_mail(
            subject=f"New Order #{data['order_id']}",
            message=f"Customer: {data['customer_email']}\nTotal: {data['total_price']}\nItems:\n{items}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
        )
    except Exception:
        log.exception("Email failed")

    ch.basic_ack(method.delivery_tag)

def main():
    logging.basicConfig(level=logging.INFO)
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn   = pika.BlockingConnection(params)
    chan   = conn.channel()
    chan.exchange_declare(exchange=EXCHANGE, exchange_type="fanout", durable=True)
    chan.queue_declare(queue=QUEUE, durable=True)
    chan.queue_bind(queue=QUEUE, exchange=EXCHANGE)
    chan.basic_qos(prefetch_count=1)
    chan.basic_consume(QUEUE, on_message_callback=handle)
    log.info("Worker ready – waiting for messages…")
    chan.start_consuming()

if __name__ == "__main__":
    main()