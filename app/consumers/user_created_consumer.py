# user-service/app/consumers/user_created_consumer.py

import logging
import json
from app.database import get_db
from app.schemas.user import UserCreate
#from app.crud.user import create_user
from app.utils.rabbitmq import RabbitMQConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def user_creation_callback(ch, method, properties, body):
    """
    Callback to handle user creation messages from RabbitMQ.
    """
    try:
        user_data = json.loads(body)
        db = next(get_db())  # Open a new DB session
        
        # Create the user with the received data
        user = UserCreate(**user_data)
       # create_user(db, user)
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"User created successfully: {user.email}")
    
    except Exception as e:
        logger.error(f"Failed to process user creation message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Optionally requeue or discard

def start_user_consuming():
    """
    Start the RabbitMQ consumer for user creation messages.
    """
    try:
        # Use the RabbitMQConnection class to handle connection
        rabbitmq = RabbitMQConnection(queue_name='user_creation_queue', exchange_name='user_events', exchange_type='fanout')
        rabbitmq.consume_messages(user_creation_callback)
        
    except Exception as e:
        logger.error(f"Error connecting to RabbitMQ: {str(e)}")
