from typing import List, Union
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import sqlalchemy as sa
from src.v1.model import Permission, PermissionType
from src.v1.base.exception import (
    AlreadyExistsError,
    DatabaseError,
    NotFoundError,
)
from .schema import CreatePermission, UpdatePermission, ValidatePermissions
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.utils.log import setup_logger

logger = setup_logger(__name__, file_path="admin.log")


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_one_permission_by_name(self, permission_name: str) -> Permission | None:
        try:
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

    async def fetch_one_permission_by_id(self, permission_id: uuid.UUID) -> Permission | None:
        try:
            logger.debug(f"Fetching permission by id: {permission_id}")
            permission = await self.db.execute(
                select(Permission).where(
                    Permission.id == permission_id
                )
            )
            result = permission.scalar_one_or_none()
            if not result:
                logger.warning(f"Permission with id '{permission_id}' not found")
                raise NotFoundError(f"Permission with id {permission_id} does not exist")
            logger.info(f"Successfully fetched permission by id: {permission_id}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching permission by id '{permission_id}': {str(e)}")
            raise DatabaseError(f"Error fetching permission: {str(e)}")

    async def fetch_all_permission(self) -> list[Permission]:
        try:
            logger.debug("Fetching all permissions")
            # do caching to prevent frequent database request since it's mostly a read operation
            permissions = await self.db.execute(select(Permission))
            result = permissions.scalars().all()
            logger.info(f"Successfully fetched {len(result)} permissions")
            data = ValidatePermissions(permissions=result).model_dump() if result else []
            return data
        except SQLAlchemyError as e:
            logger.error(f"Database error fetching all permissions: {str(e)}")
            raise DatabaseError(f"Error fetching permissions: {str(e)}")


    async def create_permission(self, permissions: Union[CreatePermission, List[CreatePermission]]) -> Union[Permission, List[Permission]]:
        if isinstance(permissions, list):
            # Bulk creation logic
            try:
                logger.info("Creating permissions...")
                existing_permissions = set()
                for p_obj in (await self.db.execute(sa.select(Permission))).scalars().all():
                    existing_permissions.add(p_obj.name)

                permissions_to_add = []
                for perm in permissions:
                    if perm.name not in existing_permissions:
                        permissions_to_add.append(Permission(name=perm.name, description=perm.description))

                created_permissions = []
                if permissions_to_add:
                    try:
                        self.db.add_all(permissions_to_add)
                        await self.db.commit()
                        for perm in permissions_to_add:
                            await self.db.refresh(perm)
                            created_permissions.append(perm)
                        logger.info(f"Added {len(created_permissions)} new permissions.")
                    except IntegrityError as e:
                        logger.warning(f"Permission already exists: {str(e)}")
                        raise AlreadyExistsError("One or more permissions already exist")
                else:
                    logger.info("No new permissions to add.")
                return created_permissions
            except (AlreadyExistsError, DatabaseError, NotFoundError):
                raise
            except SQLAlchemyError as e:
                logger.error(f"Database error during permission creation: {str(e)}")
                raise DatabaseError(f"Error creating permissions: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error during permission creation: {str(e)}")
                raise
        else:
            # Single creation logic
            try:
                logger.info(f"Creating single permission: {permissions.name}")
                # Check if permission already exists
                existing_permission = await self.db.execute(
                    select(Permission).where(Permission.name.ilike(permissions.name))
                )
                if existing_permission.scalar_one_or_none():
                    logger.warning(f"Permission '{permissions.name}' already exists")
                    raise AlreadyExistsError(f"Permission '{permissions.name}' already exists")

                new_permission = Permission(
                    name=permissions.name,
                    description=permissions.description
                )
                self.db.add(new_permission)
                await self.db.commit()
                await self.db.refresh(new_permission)
                logger.info(f"Successfully created permission: {permissions.name}")
                return new_permission
            except AlreadyExistsError:
                raise
            except IntegrityError as e:
                logger.error(f"Integrity error creating permission '{permissions.name}': {str(e)}")
                raise AlreadyExistsError(f"Permission '{permissions.name}' already exists")
            except SQLAlchemyError as e:
                logger.error(f"Database error creating permission '{permissions.name}': {str(e)}")
                raise DatabaseError(f"Error creating permission: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error creating permission '{permissions.name}': {str(e)}")
                raise

    async def update_permission(self, permission_id: uuid.UUID, update_data: UpdatePermission) -> Permission:
        try:
            logger.info(f"Updating permission with id: {permission_id}")
            permission = await self.fetch_one_permission_by_id(permission_id)

            # Update fields if provided
            if update_data.name is not None:
                # Check if new name conflicts with existing permission
                if update_data.name != permission.name:
                    existing_permission = await self.db.execute(
                        select(Permission).where(Permission.name.ilike(update_data.name))
                    )
                    if existing_permission.scalar_one_or_none():
                        logger.warning(f"Permission name '{update_data.name}' already exists")
                        raise AlreadyExistsError(f"Permission name '{update_data.name}' already exists")
                permission.name = update_data.name

            if update_data.description is not None:
                permission.description = update_data.description

            await self.db.commit()
            await self.db.refresh(permission)
            logger.info(f"Successfully updated permission: {permission_id}")
            return permission
        except (NotFoundError, AlreadyExistsError):
            raise
        except IntegrityError as e:
            logger.error(f"Integrity error updating permission '{permission_id}': {str(e)}")
            raise AlreadyExistsError("Permission name already exists")
        except SQLAlchemyError as e:
            logger.error(f"Database error updating permission '{permission_id}': {str(e)}")
            raise DatabaseError(f"Error updating permission: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating permission '{permission_id}': {str(e)}")
            raise

    async def delete_permission(self, permission_id: uuid.UUID) -> bool:
        try:
            logger.info(f"Deleting permission with id: {permission_id}")
            permission = await self.fetch_one_permission_by_id(permission_id)

            await self.db.delete(permission)
            await self.db.commit()
            logger.info(f"Successfully deleted permission: {permission_id}")
            return True
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting permission '{permission_id}': {str(e)}")
            raise DatabaseError(f"Error deleting permission: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting permission '{permission_id}': {str(e)}")
            raise
