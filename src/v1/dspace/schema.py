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

# Group dict for Super Admin
super_admin_group_dict = {
    "name": "Library Super Administrators",
    "metadata": {
        "dc.description": [
            {
                "value": "Group for super administrators with ultimate access to all system functions",
                "language": "en"
            }
        ],
        "dc.title": [
            {
                "value": "Super Administrators",
                "language": "en"
            }
        ]
    },
    "role_name": "super_admin"
}

# Group dict for User
user_group_dict = {
    "name": "Library Users",
    "metadata": {
        "dc.description": [
            {
                "value": "Group for standard library users with read-only access",
                "language": "en"
            }
        ],
        "dc.title": [
            {
                "value": "Users",
                "language": "en"
            }
        ]
    },
    "role_name": "user"
}

# Group dict for Lecturer
lecturer_group_dict = {
    "name": "Lecturers",
    "metadata": {
        "dc.description": [
            {
                "value": "Group for academic staff with permissions to create and manage resources",
                "language": "en"
            }
        ],
        "dc.title": [
            {
                "value": "Lecturers",
                "language": "en"
            }
        ]
    },
    "role_name": "lecturer"
}

# Group dict for Student
student_group_dict = {
    "name": "Students",
    "metadata": {
        "dc.description": [
            {
                "value": "Group for students with permissions to access and contribute to library resources",
                "language": "en"
            }
        ],
        "dc.title": [
            {
                "value": "Students",
                "language": "en"
            }
        ]
    },
    "role_name": "student"
}
