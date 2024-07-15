from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import user as user_router

app = FastAPI()

app.include_router(user_router.router, prefix="/users", tags=["users"])


# Serve the static directory
app.mount("/static", StaticFiles(directory="./static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the User Service!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
