from typing import Optional
from sqlalchemy import select
from src.v1.model.users import User

class UserService():
    def __init__(self):
        pass
    
    async def check_if_user_exists(self, email):
        pass 
    
    async def hash_password(self, password):
        pass 
    
    async def create_user(self, **user_data):
        pass 
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
