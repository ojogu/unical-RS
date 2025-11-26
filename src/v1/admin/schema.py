from pydantic import BaseModel
from typing import List 
class CreatePermission(BaseModel):
    name: str 
    description: str
    class Config:
        from_attributes = True
        
class CreateRole(BaseModel):
    name: str 
    description: str
    permissions: List[CreatePermission]
    class Config:
        from_attributes = True
    
class ValidatePermissions(BaseModel):
    permissions: List[CreatePermission]
    class Config:
        from_attributes = True
        
class ValidateRoles(BaseModel):
    roles: List[CreateRole]
    class Config:
        from_attributes = True



# eg data
# data = {
#     "permissions": [
#         {"name": "READ_USERS", "description": "Allows viewing user profiles."},
#         {"name": "WRITE_POSTS", "description": "Allows creating and updating content."}
#     ]
# }

# # This will now validate correctly
# validated_data = ValidatePermissions(**data) 

# # Accessing the list:
# print(validated_data.permissions)
# # Output: [CreatePermission(name='READ_USERS', ...), CreatePermission(name='WRITE_POSTS', ...)]


