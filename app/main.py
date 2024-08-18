import logging
import threading
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import StreamingResponse
from app.routes import user as user_router, review as review_router, order as order_router, wishlist as wishlist_router
from app.models import BaseModel  # Import BaseModel to ensure all models are included
from app.database import engine
from app.consumers.user_created_consumer import start_user_consuming
from app.consumers.vendor_created_consumer import start_vendor_consuming

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
app.include_router(order_router.router, prefix="/orders", tags=["orders"])
app.include_router(wishlist_router.router, prefix="/wishlist", tags=["wishlist"])

# Serve the static directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the User Service!"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    if request.method in ["POST", "PUT"]:
        body = await request.body()
        logger.info(f"Request Body: {body.decode('utf-8')}")

    response = await call_next(request)

    if isinstance(response, StreamingResponse):
        response_body = b"Streaming response not logged."
    else:
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        response.body_iterator = iter([response_body])

        response_text = response_body.decode('utf-8')
        logger.info(f"Response Body: {response_text}")

    logger.info(f"Response Status: {response.status_code}")
    return response

def start_all_consumers():
    user_thread = threading.Thread(target=start_user_consuming)
    vendor_thread = threading.Thread(target=start_vendor_consuming)
    user_thread.start()
    vendor_thread.start()
    
@app.on_event("startup")
def on_startup():
    start_all_consumers()
    logger.info("Creating all tables in the database...")
    # BaseModel.metadata.create_all(bind=engine)  # Uncomment if needed
    logger.info("All tables created successfully.")
    
    # Start the RabbitMQ consumer in a background thread
    # thread = threading.Thread(target=start_consumer, daemon=True)
    # thread.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
