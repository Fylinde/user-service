# In user-service/app/scheduled_tasks.py

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.user import UserModel
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

def cleanup_unverified_users():
    db = SessionLocal()
    try:
        # Define expiration duration, e.g., 24 hours
        expiration_period = timedelta(hours=24)
        expiration_time = datetime.utcnow() - expiration_period
        
        # Query for unverified users whose creation time is beyond the expiration period
        unverified_users = db.query(UserModel).filter(
            UserModel.is_email_verified == False,
            UserModel.created_at < expiration_time
        ).all()
        
        # Delete unverified users
        for user in unverified_users:
            logger.info(f"Deleting unverified user {user.email} created at {user.created_at}")
            db.delete(user)
        db.commit()
        logger.info("Cleanup of unverified users completed")

    finally:
        db.close()

# Initialize scheduler in main.py or an equivalent startup file
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_unverified_users, "interval", hours=24)
scheduler.start()
