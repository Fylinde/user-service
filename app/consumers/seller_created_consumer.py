import pika
import json
import logging
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.seller import SellerModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seller_callback(ch, method, properties, body):
    try:
        seller_data = json.loads(body)

        # Log the received message
        logger.info(f"Received seller_created event from RabbitMQ for seller_id: {seller_data['id']}")

        # Save seller to the local database
        db = SessionLocal()
        try:
            # Idempotency check: ensure the seller doesn't already exist
            existing_seller = db.query(SellerModel).filter(SellerModel.id == seller_data["id"]).first()
            if existing_seller:
                logger.info(f"seller with id {seller_data['id']} already exists in user-service. Skipping insertion.")
            else:
                logger.info(f"No existing seller found. Proceeding to add seller with id {seller_data['id']}.")
                seller_obj = SellerModel(
                    id=seller_data["id"],
                    name=seller_data["name"],
                    email=seller_data["email"],
                    description=seller_data.get("description"),
                    rating=seller_data.get("rating"),
                    profile_picture=seller_data.get("profile_picture"),
                    preferences=seller_data.get("preferences"),
                    hashed_password=seller_data["hashed_password"],
                )
                db.add(seller_obj)
                db.commit()
                logger.info(f"seller added in user-service: {seller_obj.name} (ID: {seller_obj.id})")
        except IntegrityError as e:
            logger.error(f"Integrity error occurred while adding seller: {str(e)}")
            db.rollback()
        except Exception as e:
            logger.error(f"Failed to add seller: {str(e)}")
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error processing seller_created message: {str(e)}")

def start_seller_consuming():
    logger.info('Connecting to RabbitMQ for seller creation messages')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()

    # Declare the fanout exchange
    channel.exchange_declare(exchange='seller_events', exchange_type='fanout')
    logger.info('Declared exchange seller_events')

    # Declare a unique queue for this consumer and bind it to the exchange
    queue_name = channel.queue_declare(queue='', exclusive=True).method.queue
    channel.queue_bind(exchange='seller_events', queue=queue_name)
    logger.info('Waiting for seller messages in user-service. To exit press CTRL+C')

    channel.basic_consume(
        queue=queue_name, on_message_callback=seller_callback, auto_ack=True
    )
    channel.start_consuming()
