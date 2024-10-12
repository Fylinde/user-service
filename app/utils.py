from passlib.context import CryptContext
import requests
from fastapi import HTTPException
from app.config import settings

ADDRESS_SERVICE_URL = settings.ADDRESS_SERVICE_URL

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user_addresses(user_id: int):
    """
    Fetch the list of addresses for a given user from the Address Service with a timeout.
    """
    try:
        response = requests.get(f"{ADDRESS_SERVICE_URL}/{user_id}", timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching addresses")
    
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Request to Address Service timed out")
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Address Service: {str(e)}")



def add_address_to_user(user_id: int, address_data: dict):
    """
    Add a new address for the user by making a POST request to the Address Service.
    """
    try:
        # Send the address data to the Address Service
        response = requests.post(f"{ADDRESS_SERVICE_URL}/", json=address_data)
        
        # If the response status code is 201 (Created), return the new address
        if response.status_code == 201:
            return response.json()
        else:
            # If the status code is not 201, raise an HTTPException
            raise HTTPException(status_code=response.status_code, detail="Error adding address")
    
    except requests.exceptions.RequestException as e:
        # Handle request errors (e.g., connection issues, timeouts, etc.)
        raise HTTPException(status_code=500, detail=f"Failed to connect to Address Service: {str(e)}")