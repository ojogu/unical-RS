from typing import List, Any
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
    def __init__(self, db: AsyncSession):
        self.db = db
    
    
    

class SuperAdminService():
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============ User Operations ============
    async def fetch_user(self, user_id: str) -> User:
        try:
            logger.debug(f"Fetching user: {user_id}")
            user = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            result = user.scalar_one_or_none()
            if not result:
                logger.warning(f"User '{user_id}' not found")
                raise NotFoundError(f"User '{user_id}' does not exist")
            logger.info(f"Successfully fetched user: {user_id}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching user '{user_id}': {str(e)}")
            raise DatabaseError(f"Error fetching user: {str(e)}")
    
    # ============ Role Operations ============
    async def check_if_roles_exist(self, role_name: str) -> Role | None:
        try:
            logger.debug(f"Checking if role exists: {role_name}")
            role = await self.db.execute(
                select(Role).where(Role.name == role_name)
            )
            result = role.scalar_one_or_none()
            if result:
                logger.info(f"Role '{role_name}' found")
            else:
                logger.debug(f"Role '{role_name}' not found")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error checking if role '{role_name}' exists: {str(e)}")
            raise DatabaseError(f"Error checking role existence: {str(e)}")
    
    async def create_roles(self, role_data: CreateRole):
        try:
            logger.debug(f"Starting to create role: {role_data.name}")
            #put user_id later on
            # validated_role_data = CreateRole(**role_data)
            
            #check if role exist 
            is_existing = await self.check_if_roles_exist(role_data.name)
            if is_existing:
                logger.warning(f"Role '{role_data.name}' already exists")
                raise AlreadyExistsError(f"'{role_data.name}' Role already exist")
            
            #fetch the user trying to create a role, to verify if his role has the permission
            # user = await self.fetch_user(user_id)
            
            # user_permission = await self.get_user_permissions(user.id)
            # if PermissionType.CREATE_ROLE not in user_permission:
            #     raise AuthorizationError()
            
            
            #validate and convert permission into a list i.e to handle roles with multiple permission
            validate_permission:ValidatePermissions = ValidatePermissions(permissions=role_data.permissions)
            permission_list = validate_permission.permissions if hasattr(validate_permission, 'permissions') else list(validate_permission)
            
            # list to hold the actual Permission model instances
            existing_permissions = []
            
            #loop through the permission list
            for permission in permission_list:
                permission_exist = await self.fetch_one_permission(permission.name)
                if not permission_exist:
                    logger.warning(f"Permission '{permission.name}' does not exist")
                    raise NotFoundError(f"{permission.name} permission does not exist")
                
                existing_permissions.append(permission_exist)
            
            #creates roles with it's permission
            logger.debug(f"Creating role with data - Name: {role_data.name}, Description: {role_data.description}")
            logger.debug(f"Permissions to assign: {existing_permissions}")
            
            new_role = Role(
                name=role_data.name,
                description = role_data.description,
                permissions = existing_permissions
            )
            self.db.add(new_role)
            await self.db.commit()
            
            logger.debug(f"Role object created: {new_role.to_dict()}")
            return new_role
        except (AlreadyExistsError, NotFoundError, AuthorizationError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error creating role '{role_data.name}': {str(e)}")
            raise DatabaseError(f"Error creating role: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating role '{role_data.name}': {str(e)}")
            raise
        
    async def fetch_one_role(self, role_name: str) -> Role | None:
        try:
            logger.debug(f"Fetching role: {role_name}")
            role = await self.db.execute(
                select(Role).where(Role.name.ilike(role_name))
            )
            result = role.scalar_one_or_none()
            if not result:
                logger.warning(f"Role '{role_name}' not found")
                raise NotFoundError(f"Role '{role_name}' does not exist")
            logger.info(f"Successfully fetched role: {role_name}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching role '{role_name}': {str(e)}")
            raise DatabaseError(f"Error fetching role: {str(e)}")
    
    async def fetch_all_roles(self) -> list[Role]:
        try:
            #TODO return the permissions too
            logger.debug("Fetching all roles")
            roles = await self.db.execute(select(Role))
            result = roles.scalars().all()
            logger.info(f"Successfully fetched {len(result)} roles")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching all roles: {str(e)}")
            raise DatabaseError(f"Error fetching roles: {str(e)}")
    
    # ============ Permission Operations ============
    async def fetch_one_permission(self, permission_name: str) -> Permission | None:
        try:
            #TODO return the permissions too
            logger.debug(f"Fetching permission: {permission_name}")
            permission = await self.db.execute(
                select(Permission).where(
                    Permission.name.ilike(permission_name)
                )
            )
            result = permission.scalar_one_or_none()
            if not result:
                logger.warning(f"Permission '{permission_name}' not found")
                raise NotFoundError(f"{permission_name} does not exist")
            logger.info(f"Successfully fetched permission: {permission_name}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching permission '{permission_name}': {str(e)}")
            raise DatabaseError(f"Error fetching permission: {str(e)}")
    
    async def fetch_all_permission(self) -> list[Permission]:
        try:
            logger.debug("Fetching all permissions")
            #do caching to prevent frequent database request since it's mostly a read operation  
            permissions = await self.db.execute(select(Permission))
            result = permissions.scalars().all()
            logger.info(f"Successfully fetched {len(result)} permissions")
            data= ValidatePermissions(permissions=result).model_dump() if result else []
            return data
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching all permissions: {str(e)}")
            raise DatabaseError(f"Error fetching permissions: {str(e)}")
    
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
        
        
        
        
        
        
#TODO: create super admin and give all permission.
#TODO: work on authentication and authorization, protected endpoints. Login/logout. Registration for normal users (students/lecturer), super admin/admin creating roles like libarians etc
#TODO: work on authentication and authorization, protected endpoints.


        
    