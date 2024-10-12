from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import BaseModel
from app.models.association_tables import group_permissions

class PermissionModel(BaseModel):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    groups = relationship("GroupModel", secondary=group_permissions, back_populates="permissions")

