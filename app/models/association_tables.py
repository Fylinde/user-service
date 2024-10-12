# app/models/association_tables.py

from sqlalchemy import Table, Column, ForeignKey
from app.database import BaseModel

group_permissions = Table(
    'group_permissions', BaseModel.metadata,
    Column('group_id', ForeignKey('groups.id'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id'), primary_key=True)
)

user_groups = Table(
    'user_groups', BaseModel.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('group_id', ForeignKey('groups.id'), primary_key=True)
)
