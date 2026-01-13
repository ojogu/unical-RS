from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.v1.model import User, Role
from src.v1.base.exception import (
    DatabaseError,
    NotFoundError,
)
from sqlalchemy.exc import SQLAlchemyError
from src.utils.log import setup_logger

logger = setup_logger(__name__, file_path="admin.log")


class UserManagementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_user(self, user_id: str) -> User:
        try:
            logger.debug(f"Fetching user: {user_id}")
            user = await self.db.execute(
                select(User).options(selectinload(User.roles).selectinload(Role.permissions)).where(User.id == user_id)
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