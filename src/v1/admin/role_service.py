from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.v1.dspace.schema import CreateGroup
from src.v1.model import Role, Permission
from src.v1.base.exception import (
    AlreadyExistsError,
    DatabaseError,
    NotFoundError,
    AuthorizationError
)
from src.v1.dspace.service import DspaceGroupService
from .schema import CreateRole
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.utils.log import setup_logger

logger = setup_logger(__name__, file_path="admin.log")


class RoleService:
    def __init__(self, db: AsyncSession, dspace_group_service:DspaceGroupService):
        self.db = db
        self.dspace_group_service = dspace_group_service

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

            # check if role exist
            is_existing = await self.check_if_roles_exist(str(role_data.name))
            if is_existing:
                logger.warning(f"Role '{role_data.name}' already exists")
                raise AlreadyExistsError(f"'{role_data.name}' Role already exist")

            # validate and convert permission into a list i.e to handle roles with multiple permission
            permission_list = [role_data.permissions] if not isinstance(role_data.permissions, list) else role_data.permissions
  
            # list to hold the actual Permission model instances
            existing_permissions = []

            # loop through the permission list
            for permission in permission_list:
                permission_exist = await self.fetch_one_permission(permission)
                if not permission_exist:
                    logger.warning(f"Permission '{permission}' does not exist")
                    raise NotFoundError(f"{permission} permission does not exist")

                existing_permissions.append(permission_exist)

            # creates roles with it's permission
            logger.debug(f"Creating role with data - Name: {role_data.name}, Description: {role_data.description}")
            logger.debug(f"Permissions to assign: {existing_permissions}")
            #create on dspace system
            group_data_dict = {
                "name": role_data.group_data.name,
                "metadata": role_data.group_data.metadata,

            }
            dspace_group = await self.dspace_group_service.create_group(CreateGroup(**group_data_dict))
            
            
            new_role = Role(
                name=role_data.name,
                description=role_data.description,
                permissions=existing_permissions,
                dspace_group_id = dspace_group["id"]
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

    async def fetch_role_with_permission(self, role_name: str):
        roles = await self.db.execute(
            select(Role).options(selectinload(Role.permissions)).where(Role.name.ilike(role_name))
        )
        result = roles.scalar_one_or_none()
        if not result:
            logger.warning(f"Role '{role_name}' not found")
            raise NotFoundError(f"Role '{role_name}' does not exist")
        logger.info(f"Successfully fetched role with permissions: {role_name}")
        role_data = {
            "role": result.to_dict(),
            "permissions": [
                {"id": p.id, "name": p.name, "description": p.description} for p in result.permissions
            ]}
        return role_data

    async def fetch_all_roles(self) -> list[Role]:
        try:
            logger.debug("Fetching all roles")
            roles = await self.db.execute(
                select(Role).options(selectinload(Role.permissions))
            )
            result = roles.scalars().all()
            logger.info(f"Successfully fetched {len(result)} roles")
            if not result:
                return []
            data_to_serialize = []
            for role in result:
                role_data = {
                    "role": role.to_dict(),
                    "permissions": [
                        {"id": p.id, "name": p.name, "description": p.description} for p in role.permissions
                    ]}
                data_to_serialize.append(role_data)
            logger.info(f"role data: {role_data}")
            return data_to_serialize

        except SQLAlchemyError as e:
            logger.error(f"Database error fetching all roles: {str(e)}")
            raise DatabaseError(f"Error fetching roles: {str(e)}")

    async def fetch_one_permission(self, permission_id: uuid.UUID):
        # Use PermissionService
        from .permission_service import PermissionService
        permission_service = PermissionService(self.db)
        return await permission_service.fetch_one_permission_by_id(permission_id)


#TODO: fix roles and group service/endpoint, assign permissions to roles when creating it using permission id, also write to dspace group for that role. 
#TODO: 