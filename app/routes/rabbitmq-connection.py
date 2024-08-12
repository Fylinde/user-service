import pika
import json
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import UserModel
from app.routes.user import create_user_in_database
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ connection setup
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='user_created')

def on_message(ch, method, properties, body):
    db: Session = next(get_db())
    user_data = json.loads(body)
    try:
        create_user_in_database(user_data, db)
    except Exception as e:
        logger.error(f"Failed to create user: {e}")

channel.basic_consume(queue='user_created', on_message_callback=on_message, auto_ack=True)

def start_consuming():
    logger.info("Starting to consume from the user_created queue")
    channel.start_consuming()

@app.on_event("startup")
def startup_event():
    # Start the RabbitMQ consumer in a background thread
    import threading
    thread = threading.Thread(target=start_consuming, daemon=True)
    thread.start()

@app.get("/")
def read_root():
    return {"message": "User service is running"}

