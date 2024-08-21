import pika
import json
import logging
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models.user import UserModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def user_callback(ch, method, properties, body):
    user_data = json.loads(body)

    # Log the received message
    logger.info(f"Received user_created event from RabbitMQ for user_id: {user_data['id']}")

    # Save user to the local database
    db = SessionLocal()
    try:
        # Idempotency check: ensure the user doesn't already exist
        logger.info(f"Checking if user with id {user_data['id']} already exists...")
        existing_user = db.query(UserModel).filter(UserModel.id == user_data["id"]).first()
        if existing_user:
            logger.info(f"User with id {user_data['id']} already exists. Skipping insertion.")
        else:
            logger.info(f"No existing user found. Proceeding to add user with id {user_data['id']}.")
            user_obj = UserModel(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=user_data["hashed_password"],
                profile_picture=user_data.get("profile_picture"),
                preferences=user_data.get("preferences"),
                is_active=user_data.get("is_active", True),
                role=user_data.get("role", "user"),
                two_factor_enabled=user_data.get("two_factor_enabled", False),
                two_factor_secret=user_data.get("two_factor_secret"),
                password_last_updated=user_data.get("password_last_updated"),
                failed_login_attempts=user_data.get("failed_login_attempts", 0),
                account_locked=user_data.get("account_locked", False),
                backup_codes=user_data.get("backup_codes"),
            )
            db.add(user_obj)
            db.commit()
            logger.info(f"User added in user-service: {user_obj.username} (ID: {user_obj.id})")
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while adding user: {str(e)}")
        db.rollback()
    except Exception as e:
        logger.error(f"Failed to add user: {str(e)}")
        db.rollback()
    finally:
        db.close()

def start_user_consuming():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()

    # Declare the fanout exchange
    channel.exchange_declare(exchange='user_events', exchange_type='fanout')

    # Declare a unique queue for this consumer and bind it to the exchange
    queue_name = channel.queue_declare(queue='', exclusive=True).method.queue
    channel.queue_bind(exchange='user_events', queue=queue_name)

    channel.basic_consume(
        queue=queue_name, on_message_callback=user_callback, auto_ack=True
    )

    logger.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
