from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Enum as SqlEnum, Integer, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from datetime import datetime
from src.v1.base.model import BaseModel
from .roles import user_roles, Role


class User(BaseModel):
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    dspace_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    dspace_special_group: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool]=mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool]=mapped_column(Boolean, default=False, nullable=False)
    
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_roles,
        backref="users",
        lazy="selectin"
    )


class Resource(BaseModel):
    pass

class MetaData(BaseModel):
    pass
