import uuid
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

class GroupParams(BaseModel):
    user_id: uuid.UUID
    group_id: uuid.UUID
    group_name: str

# Minimal test data example
# test_group_data = CreateGroup(
#     name="Library Administrators",
#     metadata={
#         "dc.description": [
#             MetadataEntry(
#                 value="Group for library administrators with full access",
#                 language="en"
#             )
#         ],
#         "dc.title": [
#             MetadataEntry(
#                 value="Administrators",
#                 language="en"
#             )
#         ]
#     },
#     role_name=Role_Enum.ADMIN
# )

# # As dictionary
# test_group_dict = {
#     "name": "Library Administrators",
#     "metadata": {
#         "dc.description": [
#             {
#                 "value": "Group for library administrators with full access",
#                 "language": "en"
#             }
#         ],
#         "dc.title": [
#             {
#                 "value": "Administrators",
#                 "language": "en"
#             }
#         ]
#     },
#     "role_name": "admin"
# }