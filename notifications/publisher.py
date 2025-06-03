import json, pika
from django.conf import settings

EXCHANGE = "si.orders"

def publish_order_created(order):
    params = pika.URLParameters(settings.RABBITMQ_URL)
    conn   = pika.BlockingConnection(params)
    chan   = conn.channel()
    chan.exchange_declare(exchange=EXCHANGE, exchange_type="fanout", durable=True)

    payload = {
        "order_id":      order.id,
        "customer_email":order.customer.email,
        "customer_phone":order.customer.phone_number,
        "total_price":   str(order.total_price),
        "items": [
            {"product_id":i.product.id,
             "name":i.product.name,
             "quantity":i.quantity,
             "unit_price":str(i.unit_price),
             "line_price":str(i.line_price),
            }
            for i in order.items.all()
        ],
        "created_at": order.created_at.isoformat(),
    }
    chan.basic_publish(
        exchange=EXCHANGE,
        routing_key="",        # fanout ignores routing key
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    conn.close()