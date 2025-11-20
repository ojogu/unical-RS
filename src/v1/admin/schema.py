from pydantic import BaseModel

class CreateRole(BaseModel):
    name:str
    description:str
    
class CreatePermission(BaseModel):
    name: set[str]
    description: set[str]
    
class ValidatePermissions(BaseModel):
    data: CreatePermission[list]