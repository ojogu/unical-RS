from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.log import setup_logger
from src.v1.base.exception import (
    DatabaseError, 
    NotFoundError,
    AlreadyExistsError
    )
from src.v1.model.users import User
from src.v1.auth.schema import CreateUser, Login
from src.v1.auth.service import password_hash, verify_password

logger = setup_logger(__name__, file_path="user.log")


class UserService:
    # this is for normal users activities
    def __init__(self, db: AsyncSession):
        self.db = db

    async def hash_password(self, password):
        pass

    async def create_user(self, user_data: CreateUser):

        
        #admin have a different endpoint, future update(wait for approval by super admin, or another admin)
        #student/lecturer share one endpoint, use school api to verify authencity
        #  school provides an api for id verification, call the service. for lecturers to get info like dept, name, etc 
        user = await self.get_user_by_email(user_data.email)
        if user:
            raise AlreadyExistsError()
        
        #hash password
        password = password_hash(user_data.password)
        user_data.password = password
        
        #write to dspace
        
        #write to our db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        try:
            logger.info(f"Fetching user with email: {email}")
            result = await self.db.execute(
                select(User).where(User.email == email.lower())
            )
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email: {email} - {str(e)}")
            raise DatabaseError()
        
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetch a user by their id."""
        try:
            logger.info(f"Fetching user with id: {user_id}")
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email: {user_id} - {str(e)}")
            raise DatabaseError()

    async def authenticate_user(user_data: Login):
        pass 