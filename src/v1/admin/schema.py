import uuid
from pydantic import BaseModel
from typing import List, Union, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.v1.dspace.schema import CreateGroup

class CreatePermission(BaseModel):
    id: Optional[uuid.UUID] = None
    name: str
    description: str
    class Config:
        from_attributes = True

class UpdatePermission(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    class Config:
        from_attributes = True
        
class CreateRole(BaseModel):
    name: str
    description: str
    permissions: Union[uuid.UUID, List[uuid.UUID]]
    group_data: "CreateGroup"
    
    class Config:
        from_attributes = True
    
class ValidatePermissions(BaseModel):
    permissions: List[CreatePermission]
    class Config:
        from_attributes = True
        
# class ValidateRoles(BaseModel):
#     roles: List["CreateGroup"]  # Forward reference since CreateGroup is in another module
#     class Config:
#         from_attributes = True



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
