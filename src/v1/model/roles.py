from sqlalchemy import Column, ForeignKey, String, Table, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.v1.base.model import BaseModel
from enum import StrEnum


class PermissionType(StrEnum):
    # Admin operations
    CREATE_ROLE = "create.role"
    READ_ROLE = "read.role"
    UPDATE_ROLE = "update.role"
    DELETE_ROLE = "delete.role"
    
    # Resource operations
    CREATE_RESOURCE = "create.resource"
    READ_RESOURCE = "read.resource"
    UPDATE_RESOURCE = "update.resource"
    DELETE_RESOURCE = "delete.resource"
    
    # Management operations
    APPROVE_SUBMISSION = "approve.submission"
    MANAGE_COLLECTION = "manage.collection"
    EDIT_METADATA = "edit.metadata"

PERMISSION_DESCRIPTIONS = {
    PermissionType.CREATE_ROLE: "Create roles",
    PermissionType.READ_ROLE: "Read roles",
    PermissionType.UPDATE_ROLE: "Update roles",
    PermissionType.DELETE_ROLE: "Delete roles",
    PermissionType.CREATE_RESOURCE: "Create library resources",
    PermissionType.READ_RESOURCE: "Read library resources",
    PermissionType.UPDATE_RESOURCE: "Update library resources",
    PermissionType.DELETE_RESOURCE: "Delete library resources",
    PermissionType.APPROVE_SUBMISSION: "Approve submissions",
    PermissionType.MANAGE_COLLECTION: "Manage collections",
    PermissionType.EDIT_METADATA: "Edit metadata",
}

class Role_Enum(StrEnum):
    ADMIN = "admin"
    USER = "user"
    SUPER_ADMIN = "super_admin"
    LECTURER = "lecturer"
    STUDENT = "student"
    
#junction table (users->roles)
user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

#junction table (roles->permission)
role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


#many to many relation with permission
class Role(BaseModel):
    name: Mapped[Role_Enum] = mapped_column(
        SqlEnum(Role_Enum, name="role_enum"),  nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", secondary=role_permissions, backref="roles", lazy="selectin"
    )


class Permission(BaseModel):
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)







# Role and Permission Management Module
# This module defines the role-based access control (RBAC) system for the library management system.
# It includes permission types, role and permission models, and their relationships.
# Classes:
#     PermissionType: A class containing all available permission constants used throughout the system.
#         Permissions are organized into three categories:
#         - Admin operations: Create, Read, Update, Delete roles
#         - Resource operations: Create, Read, Update, Delete library resources
#         - Management operations: Approve submissions, manage collections, edit metadata
#     Role: A database model representing a role entity with associated permissions.
#         Attributes:
#             name (str): Unique name of the role, indexed for efficient querying.
#             description (str): Optional description of the role's purpose.
#             permissions: Many-to-many relationship to Permission objects.
#     Permission: A database model representing a granular permission that can be assigned to roles.
#         Attributes:
#             name (str): Unique name of the permission, indexed for efficient querying.
# Tables:
#     user_roles: Association table for the many-to-many relationship between users and roles.
#     role_permissions: Association table for the many-to-many relationship between roles and permissions.
# Module-level Constants:
#     PERMISSION_DESCRIPTIONS (dict): A mapping of permission names to human-readable descriptions.
# Note:
#     The module includes raw SQL for seeding the permissions table with initial permission records.
#     Ensure all permissions defined in PermissionType are inserted into the database before use.


"""

"""
