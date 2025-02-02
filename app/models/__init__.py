
from app.models.user import UserModel
#from app.models.product import ProductModel
from app.models.review import ReviewModel
#from app.models.order import OrderModel  # Assuming there's an Order model
from app.models.wishlist import WishlistModel  # Assuming there's a Wishlist model
from app.models.seller import SellerModel  # Assuming there's a seller model
from app.models.group import GroupModel
#from app.models.address import AddressModel
from app.models.customer_events import CustomerEventModel
from app.models.customer_notes import CustomerNoteModel
from app.models.permissions import PermissionModel
from app.models.association_tables import group_permissions, user_groups  # Include association tables
from app.models.staff import StaffNotificationRecipientModel
from app.database import BaseModel
from app.models.ai_recommendation import AIRecommendationModel
from app.models.notification import NotificationModel

__all__ = ["UserModel", 
    
           "ReviewModel", 
      
           "WishlistModel", 
           "SellerModel", 
           "BaseModel", 
           "StaffNotificationRecipientModel",
           "group_permissions",
           "user_groups",
           "PermissionModel",
           "CustomerNoteModel",
           "CustomerEventModel",
        
           "GroupModel", 
           "AIRecommendationModel",
           "NotificationModel"
           ]
