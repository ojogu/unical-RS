from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field
# from src.v1.admin.schema import CreateRole
from src.v1.model.roles import Role_Enum
class Token(BaseModel):
    user: Dict[str, Any]
    exp: datetime
    jti: str 
    refresh: bool
    
class CreateUser(BaseModel):
    user_name:str
    email:str
    first_name:str
    last_name:str
    password:str
    role: Role_Enum
    
class Login(BaseModel):
    email:EmailStr
    password:str 
    

class MetadataValue(BaseModel):
    value: str
    language: Optional[str] = None
    authority: Optional[str] = ""
    confidence: int = -1

class EPersonMetadata(BaseModel):
    eperson_firstname: List[MetadataValue] = Field(..., alias="eperson.firstname")
    eperson_lastname: List[MetadataValue] = Field(..., alias="eperson.lastname")

class EPersonCreate(BaseModel):
    name: str
    metadata: EPersonMetadata
    canLogIn: bool = True
    email: str
    requireCertificate: bool = False
    selfRegistered: bool = True
    type: str = "eperson"

# payload = EPersonCreate(
#     name="user@institution.edu",
#     email="user@institution.edu",
#     canLogIn=True,
#     selfRegistered=True,
#     metadata={
#         "eperson.firstname": [{"value": "John"}],
#         "eperson.lastname": [{"value": "Doe"}]
#     }
# )

# print(payload.dict(by_alias=True))
