from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.log import setup_logger
from src.v1.base.exception import (
    DatabaseError,
    NotFoundError,
    AlreadyExistsError,
    InvalidEmailPassword
    )
from src.v1.model.users import User
from src.v1.auth.schema import CreateUser, Login
from src.v1.auth.service import password_hash, verify_password
from src.v1.dspace.service import DspaceAuthService

logger = setup_logger(__name__, file_path="user.log")


class UserService:
    # this is for normal users activities
    def __init__(self, db: AsyncSession, dspace_auth_service:DspaceAuthService):
        self.db = db
        self.dspace_auth_service = dspace_auth_service


    async def create_user(self, user_data: CreateUser):
        
        #  school provides an api for id verification, call the service. for lecturers to get info like dept, name, etc 
        user = await self.get_user_by_email(user_data.email)
        if user:
            raise AlreadyExistsError()
        
        #hash password
        password = password_hash(user_data.password)
        user_data.password = password
        
        #write to dspace; link user to group 
        
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

    async def check_if_user_exist_by_id(self, user_id: uuid.UUID) -> User:
        """Fetch a user by their id, raises NotFoundError if not found."""
        try:
            logger.info(f"Fetching user with id: {user_id}")
            user = await self.get_user_by_id(user_id)
            if not user:
                raise NotFoundError()
            return user

        except Exception as e:
            logger.error(f"Error fetching user by id: {user_id} - {str(e)}")
            raise DatabaseError()

    async def check_if_user_exist_by_email(self, email: str) -> User:
        """Fetch a user by their email, raises NotFoundError if not found."""
        try:
            logger.info(f"Fetching user with email: {email}")
            user = await self.get_user_by_email(email)
            if not user:
                raise NotFoundError()
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email: {email} - {str(e)}")
            raise DatabaseError()

    async def authenticate_user(self, user_data: Login) -> dict:
        """Authenticate user and return user data for token creation."""
        try:
            logger.info(f"Authenticating user with email: {user_data.email}")
            user = await self.get_user_by_email_strict(user_data.email)
            if not verify_password(user_data.password, user.password):
                raise InvalidEmailPassword()
            # Return user data for token
            return {
                "user_id": str(user.id),
                "email": user.email,
                "role": user.role.name if user.role else None  # Assuming user has role relationship
            }
        except Exception as e:
            logger.error(f"Error authenticating user {user_data.email}: {str(e)}")
            raise
