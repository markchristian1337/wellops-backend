import pika
import json
import pandas as pd
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.sensors.temperature import Temperature
import os
from datetime import datetime, timezone

QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME", "temp.workers")
WINDOW_SIZE = 10
EXCHANGE_NAME = os.getenv("RABBITMQ_EXCHANGE_NAME", "sensor.readings")


def get_rolling_average(db: Session, sensor_id: str) -> float:
    # fetch last WINDOW_SIZE readings for this sensor ordered by recorded_at desc
    q = (
        db.query(Temperature)
        .filter(Temperature.sensor_id == sensor_id)
        .order_by(Temperature.recorded_at.desc())
        .limit(WINDOW_SIZE)
        .all()
    )
    # extract the value column into a pandas Series
    s = pd.Series([r.value for r in q])
    if s.empty:
        return 0.0
    return float(s.mean())


def process_message(ch, method, properties, body):
    # deserialize body from JSON
    msg = json.loads(body)
    # open a db session
    db = SessionLocal()
    try:
        # calculate rolling average using get_rolling_average
        avg_value = get_rolling_average(db, msg["sensor_id"])
        # create a Temperature ORM object with all fields including avg_value
        temperature = Temperature(
            sensor_id=msg["sensor_id"],
            value=msg["value"],
            unit=msg["unit"],
            location=msg.get("location"),
            recorded_at=datetime.fromisoformat(msg["recorded_at"]),
            raw_payload=body.decode("utf-8"),
            avg_value=avg_value,
        )
        # add, commit, refresh
        db.add(temperature)
        db.commit()
        db.refresh(temperature)
        # acknowledge the message (ch.basic_ack)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        db.rollback()
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        print(f"Error processing message: {e}")
    finally:
        db.close()


def start_worker():
    rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
    rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")

    if not rabbitmq_user or not rabbitmq_pass:
        raise ValueError("RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS must be set")

    # create a pika BlockingConnection
    credentials = pika.PlainCredentials(username=rabbitmq_user, password=rabbitmq_pass)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq-service"), credentials=credentials
        )
    )
    # open a channel
    channel = connection.channel()
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="topic",
        durable=True,
    )
    # declare the queue as durable
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(
        queue=QUEUE_NAME, exchange=EXCHANGE_NAME, routing_key="temperature.*"
    )
    # set basic_qos prefetch_count=1
    channel.basic_qos(prefetch_count=1)
    # set up basic_consume pointing at process_message, auto_ack=False
    channel.basic_consume(
        queue=QUEUE_NAME, on_message_callback=process_message, auto_ack=False
    )
    # start consuming
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()
