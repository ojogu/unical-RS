from typing import Optional
from sqlalchemy import select
from src.v1.model.users import User
from src.v1.schema.auth import ClientCreate
from sqlalchemy.ext.asyncio import AsyncSession
from src.v1.base.exception import (
    AlreadyExistsError,
    DatabaseError,
    NotFoundError,
    AuthorizationError
)
from src.utils.log import setup_logger
logger = setup_logger(__name__, file_path="user.log")

class UserService():
    #this is for normal users activities
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_if_user_exists(self, email:str):
        user = await self.get_user_by_email(email) 
        if not user:
            raise NotFoundError(f"{email} does not exists")
        return user
    
    async def hash_password(self, password):
        pass 
    
    async def create_user(self, user_data:ClientCreate):
        # user = config.base_username
        # password = config.base_password
        #use the super admin cred, this is the credwe'll be using to manipulate dspace, eg able to create other users since dspace requires having an authenticated admin jwt to get token to create users on dspace ends.
        #if school provides an api for id verification, call the service.
        pass 
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        try:
            logger.info(f"Fetching user with email: {email}")
            result = await self.db.execute(
                select(User).where(User.email == email.lower())
            )
            user = result.scalar_one_or_none()
            if user:
                logger.info(f"User found with email: {email}")
            else:
                logger.debug(f"No user found with email: {email}")
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email: {email} - {str(e)}")
            raise DatabaseError(f"Error fetching user by email: {str(e)}")
