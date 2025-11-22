from pydantic import BaseModel
from typing import List 
class CreatePermission(BaseModel):
    name: str 
    description: str
class CreateRole(BaseModel):
    name: str 
    description: str
    
class ValidatePermissions(BaseModel):
    permissions: List[CreatePermission] 
    

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