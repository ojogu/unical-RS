from typing import (  # Import Generic, List, TypeVar
    Any,
    Dict
)

import sqlalchemy as sa
import uuid
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr




# Define naming conventions for database constraints
# This helps keep index and constraint names consistent and predictable.
# See: https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)

class Base(DeclarativeBase):
    metadata = metadata

class BaseModel(Base):
    """Base class for all SQLAlchemy models."""
    
    __abstract__ = True
    # Optional: Define common columns or methods for all models
    id = sa.Column(sa.UUID, primary_key=True, default=uuid.uuid4)
    created_at = sa.Column(sa.DateTime(timezone=True), default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now())
    deleted_at = sa.Column(sa.DateTime, nullable=True)


    # Example: Automatically generate table names
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Converts CamelCase class name to snake_case table name
        import re

        name = cls.__name__
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
        return name + "s"  # Pluralize table names


    def to_dict(self) -> Dict[str, Any]:
        """Converts the SQLAlchemy model instance to a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    
    # Example: Common primary key
    # id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Example: Common timestamp columns
    # created_at: Mapped[datetime] = mapped_column(
    #     server_default=func.now(), nullable=False
    # )
    # updated_at: Mapped[datetime] = mapped_column(
    #     server_default=func.now(), onupdate=func.now(), nullable=False
    # )





