from typing import List
from src.v1.model import User, Role, Permission, PermissionType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update

from src.v1.base.exception import (
    AlreadyExistsError,
    DatabaseError,
    NotFoundError,
    AuthorizationError
)
from .schema import CreatePermission, CreateRole, ValidatePermissions
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.utils.log import setup_logger
logger = setup_logger(__name__, file_path="admin.log")

class AdminService():
    def __init__(self):
        pass
    


class SuperAdmin():
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============ User Operations ============
    async def fetch_user(self, user_id: str) -> User | None:
        user = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return user.scalar_one_or_none()
    
    # ============ Role Operations ============
    async def check_if_roles_exist(self, role_name: str):
        role = await self.db.execute(
            select(Role).where(Role.name == role_name)
        )
        return role.scalar_one_or_none()
    
    async def create_roles(self, user_id, permission: list[str], **role_data: CreateRole):
        validated_data = CreateRole(**role_data) 
        is_existing = await self.check_if_roles_exist(validated_data.name)
        if is_existing:
            raise AlreadyExistsError(f"'{validated_data.name}' Role already exist")
        
        user = await self.fetch_user(user_id)
        if not user:
            raise NotFoundError(f"{user_id} does not exist")
        
        user_permission = await self.get_user_permissions(user_id)
        if PermissionType.CREATE_ROLE not in user_permission:
            raise AuthorizationError()
        
        validated_role_data = CreateRole(**role_data)
        validate_permission = ValidatePermissions.model_validate(permission)
        if not validated_data:
            raise NotFoundError("this permission does not exi")
    
    # ============ Permission Operations ============
    def check_if_permission_exists(self, permission: str):
        pass 
    
    # def validated_permission(self, permission_list: list):
    #     pass
    
    def create_permissions(self):
        pass 
    
    # ============ Admin Operations ============
    def create_admins(self):
        pass 
    
    # ============ Utility Operations ============
    async def get_user_permissions(self, user_id: str) -> set[str]:
        """
        Load the user, then follow relationships:
        user → roles → permissions.
        Combine all permission names into a flat set().
        """
        user = await self.fetch_user(user_id)
        if not user:
            return set()
        
        permission_set: set[str] = set()
        for role in user.roles:
            for perm in role.permissions:
                permission_set.add(perm.name)
        
        return permission_set
    
    @staticmethod
    def get_valid_permissions() -> List[str]:
        """Utility to get all defined permission string values."""
        # PermissionType.__members__.values() gives us all enum members. 
        # We use 'value' to get the string representation (e.g., "create.role").
        return [member.value for member in PermissionType]

    def validated_permission(self, permission_list: List[str]) -> bool:
        """
        Checks if ALL strings in permission_list are valid, existing 
        permissions defined in the PermissionType enum.

        Args:
            permission_list: A list of strings representing permissions to check.

        Returns:
            True if all permissions exist in PermissionType, False otherwise.
        """
        
        # Get the set of all valid permission strings from the enum for fast lookups
        valid_permissions_set = {member.value for member in PermissionType}
        
        # Check if every item in the input list is present in the set of valid permissions
        for requested_permission in permission_list:
            if requested_permission not in valid_permissions_set:
                return False
        
        # If the loop completes without returning False, all permissions are valid
        return True
        
        
        
        
        
        
        
        
    