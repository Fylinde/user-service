from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import BaseModel
from app.models.association_tables import user_groups
from app.models.permissions import group_permissions

class GroupModel(BaseModel):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)
    
    # Relationships
    users = relationship("UserModel", secondary=user_groups, back_populates="groups")
    permissions = relationship("PermissionModel", secondary=group_permissions, back_populates="groups")  # Add this line

    def __repr__(self):
        return f'<Group {self.name}>'
