from typing import List
from fastapi import Depends
from src.v1.model.users import User
from src.v1.route.util import get_current_user
from src.utils.exception import AuthorizationError
from src.utils.log import setup_logger

logger = setup_logger(__name__, "authorization.log")

class RoleCheck():
    def __init__(self, required_roles = List[str]):
        self.required_roles = required_roles
    
    def __call__(self, current_user: "User" = Depends(get_current_user)):
        logger.info(f"Role check for user {current_user.id} with roles {current_user.roles} against required roles {self.required_roles}")
        user_roles_list = [current_user.roles] if isinstance(current_user.roles, str) else current_user.roles
        
        
        access = self.has_access(self.required_roles, user_roles_list)
        if access:
            logger.info(f"Access granted for user {current_user.id}")
            return True
        else:
            logger.warning(f"Access denied for user {current_user.id}: required roles {self.required_roles}, user roles {current_user.roles}")
            raise AuthorizationError()
    

    def has_access(self, required_roles, user_role):
        # Ensure a single string role is treated as a list containing that role
        if isinstance(user_role, str):
            user_role = [user_role]
        
        if isinstance(required_roles, str):
            required_roles = [required_roles]
            
        return bool (set(user_role) & set(required_roles))