import pika
import json
import logging
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.vendor import VendorModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def vendor_callback(ch, method, properties, body):
    try:
        vendor_data = json.loads(body)

        # Log the received message
        logger.info(f"Received vendor_created event from RabbitMQ for vendor_id: {vendor_data['id']}")

        # Save vendor to the local database
        db = SessionLocal()
        try:
            # Idempotency check: ensure the vendor doesn't already exist
            existing_vendor = db.query(VendorModel).filter(VendorModel.id == vendor_data["id"]).first()
            if existing_vendor:
                logger.info(f"Vendor with id {vendor_data['id']} already exists in user-service. Skipping insertion.")
            else:
                logger.info(f"No existing vendor found. Proceeding to add vendor with id {vendor_data['id']}.")
                vendor_obj = VendorModel(
                    id=vendor_data["id"],
                    name=vendor_data["name"],
                    email=vendor_data["email"],
                    description=vendor_data.get("description"),
                    rating=vendor_data.get("rating"),
                    profile_picture=vendor_data.get("profile_picture"),
                    preferences=vendor_data.get("preferences"),
                    hashed_password=vendor_data["hashed_password"],
                )
                db.add(vendor_obj)
                db.commit()
                logger.info(f"Vendor added in user-service: {vendor_obj.name} (ID: {vendor_obj.id})")
        except IntegrityError as e:
            logger.error(f"Integrity error occurred while adding vendor: {str(e)}")
            db.rollback()
        except Exception as e:
            logger.error(f"Failed to add vendor: {str(e)}")
            db.rollback()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error processing vendor_created message: {str(e)}")

def start_vendor_consuming():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()

    # Declare the fanout exchange
    channel.exchange_declare(exchange='vendor_events', exchange_type='fanout')

    # Declare a unique queue for this consumer and bind it to the exchange
    queue_name = channel.queue_declare(queue='', exclusive=True).method.queue
    logger.info(f"Declared queue {queue_name} and binding it to vendor_events exchange")
    channel.queue_bind(exchange='vendor_events', queue=queue_name)

    channel.basic_consume(
        queue=queue_name, on_message_callback=vendor_callback, auto_ack=True
    )

    logger.info('Waiting for vendor messages. To exit press CTRL+C')
    channel.start_consuming()
