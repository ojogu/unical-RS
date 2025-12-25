from pydantic import BaseModel
from typing import Dict, List, Optional
from src.v1.model.roles import Role_Enum

class MetadataEntry(BaseModel):
    value: str
    language: Optional[str] = None
    authority: str = ""
    confidence: int = -1

    class Config:
        from_attributes = True


class CreateGroup(BaseModel):
    name: str
    metadata: Dict[str, List[MetadataEntry]]
    role_name: Role_Enum
    class Config:
        from_attributes = True
