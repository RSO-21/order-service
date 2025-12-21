import pika, json
from app.database import get_db_session as get_db
from app.models import Order
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

def get_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )

def callback(ch, method, properties, body):
    # decode and parse
    event = json.loads(body.decode('utf-8'))
    
    db = get_db()
    try:
        # DB logic
        order = db.query(Order).filter(Order.id == event["order_id"]).first()
        if order:
            order.payment_status = event["payment_status"]
            order.order_status = "CONFIRMED" if event["payment_status"] == "PAID" else "CANCELLED"
            db.commit()
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")

def start_consumer():
    connection = get_connection()
    channel = connection.channel()

    # Durable=True ensures the queue survives a RabbitMQ restart
    channel.queue_declare(queue='payment_confirmed', durable=True)
    
    # Fair dispatch: don't give a worker more than one message at a time
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(queue='payment_confirmed', on_message_callback=callback)
    
    print("Order Service listening...")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()