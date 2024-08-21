from sqlalchemy.orm import Session
from app.models.order import OrderModel
from app.models.product import ProductModel
from app.schemas.order import OrderCreate

def create_order(db: Session, order: OrderCreate, user_id: int):
    db_order = OrderModel(
        user_id=user_id,
        product_id=order.product_id,
        quantity=order.quantity,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders_by_user(db: Session, user_id: int):
    return db.query(OrderModel).filter(OrderModel.user_id == user_id).all()
