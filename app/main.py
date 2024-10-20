import logging
import threading
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import (
    user as user_router, 
    review as review_router, 
    wishlist as wishlist_router
   
)
from app.consumers.user_created_consumer import start_user_consuming
from app.consumers.vendor_created_consumer import start_vendor_consuming
import pika
from app.config import settings
from app.tasks.cleanup import scheduler, cleanup_expired_unverified_users  # Import the scheduler to 
from apscheduler.schedulers.base import SchedulerAlreadyRunningError
from fastapi.middleware.cors import CORSMiddleware


# Initialize the scheduler at a module level
#scheduler = BackgroundScheduler()

logger = logging.getLogger(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

# Initialize FastAPI with metadata for Swagger
app = FastAPI(
    title="User Service API",
    description="API documentation for the User Service, which manages user data, reviews, orders, and wishlists.",
    version="1.0.0",
    openapi_tags=[
        {"name": "users", "description": "Operations related to managing users"},
        {"name": "reviews", "description": "Operations related to managing reviews"},
        {"name": "orders", "description": "Operations related to managing orders"},
        {"name": "wishlist", "description": "Operations related to managing wishlists"},
    ],
)

# Include routers
app.include_router(user_router.router, prefix="/users", tags=["users"])
app.include_router(review_router.router, prefix="/reviews", tags=["reviews"])
app.include_router(wishlist_router.router, prefix="/wishlist", tags=["wishlist"])

# Serve the static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Define the list of allowed origins explicitly
origins = [
    "http://localhost:3000",  # Your frontend application
]


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow these origins
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Start all consumers for user-service and vendor-service
def start_all_consumers():
    try:
        user_thread = threading.Thread(target=start_user_consuming)
        user_thread.start()
        vendor_thread = threading.Thread(target=start_vendor_consuming)
        vendor_thread.start()
        logger.info("All consumers started successfully.")
    except Exception as e:
        logger.error(f"Error while starting consumers: {str(e)}")

# Add FastAPI startup event to start consumers
@app.on_event("startup")
async def startup_event():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
        )
        connection.close()
        logger.info("Successfully connected to RabbitMQ")
    except Exception as e:
       
        logger.error(f"Failed to connect to RabbitMQ: {e}")
    
    start_all_consumers()
    
    for route in app.router.routes:
        print(route.path, route.name)
       # Ensure the scheduler is running when the app starts
    try:
        # Check if the scheduler is already running before starting
        if not scheduler.running:
            scheduler.add_job(cleanup_expired_unverified_users, 'interval', hours=24)

            scheduler.start()
            logger.info("Scheduler started for cleaning up unverified users.")
        else:
            logger.info("Scheduler is already running.")
    except SchedulerAlreadyRunningError:
        logger.warning("Attempted to start the scheduler, but it was already running.")
    except Exception as e:
        logger.error(f"Error occurred while starting the scheduler: {e}")
        
@app.get("/")
def read_root():
    return {"message": "Welcome to the User Service!"}
