from fastapi import APIRouter, Depends, status
from typing import Union

from src.v1.route.util import get_permission_service
# from .service import SuperAdminService, AdminService
from .permission_service import PermissionService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import CreatePermission, UpdatePermission, CreateRole, ValidatePermissions
from src.v1.dspace.schema import CreateGroup
from src.utils.response import success_response
from src.utils.log import setup_logger
logger = setup_logger(__name__, file_path="admin.log")





# Super Admin Router
super_admin_router = APIRouter(
    # prefix="/super-admin",
    # tags=["super-admin"]
)




#permission
@super_admin_router.get("/permission")
async def fetch_all_permission(permission_service: PermissionService = Depends(get_permission_service)):
    permission = await permission_service.fetch_all_permission()
    return permission

@super_admin_router.post("/permission")
async def create_permission(
    permission_data: Union[CreatePermission, list[CreatePermission]],
    permission_service: PermissionService = Depends(get_permission_service)
):
    result = await permission_service.create_permission(permission_data)
    if isinstance(result, list):
        data = [CreatePermission(id=perm.id, name=perm.name, description=perm.description) for perm in result]
    else:
        data = CreatePermission(id=result.id, name=result.name, description=result.description)
    response = success_response(
        status_code=status.HTTP_201_CREATED,
        data=data
    )
    return response

@super_admin_router.get("/permission/{permission_id}")
async def fetch_permission_by_id(
    permission_id: str,
    permission_service: PermissionService = Depends(get_permission_service)
):
    permission = await permission_service.fetch_one_permission_by_id(permission_id)
    response = success_response(
        status_code=status.HTTP_200_OK,
        data={
            "id": str(permission.id),
            "name": permission.name,
            "description": permission.description
        }
    )
    return response

@super_admin_router.put("/permission/{permission_id}")
async def update_permission(
    permission_id: str,
    update_data: UpdatePermission,
    permission_service: PermissionService = Depends(get_permission_service)
):
    updated_permission = await permission_service.update_permission(permission_id, update_data)
    response = success_response(
        status_code=status.HTTP_200_OK,
        data={
            "id": str(updated_permission.id),
            "name": updated_permission.name,
            "description": updated_permission.description
        }
    )
    return response

@super_admin_router.delete("/permission/{permission_id}")
async def delete_permission(
    permission_id: str,
    permission_service: PermissionService = Depends(get_permission_service)
):
    await permission_service.delete_permission(permission_id)
    response = success_response(
        status_code=status.HTTP_200_OK,
        message="Permission deleted successfully"
    )
    return response


# @super_admin_router.post("/role")
# #auth decorator here
# async def create_role(data:CreateGroup,
# super_admin_service:SuperAdminService = Depends(get_super_admin_service)
# ):
#     new_role =  await super_admin_service.create_roles(data)
#     response = success_response(
#         status_code=status.HTTP_201_CREATED,
#         data = new_role.to_dict()
#     )
#     return response

# @super_admin_router.get("/fetch-role")
# #auth decorator here
# async def fetch_all_roles(
# super_admin_service:SuperAdminService = Depends(get_super_admin_service)
# ):
#     roles =  await super_admin_service.fetch_all_roles()
#     if not roles:
#         response = success_response(
#             status_code=status.HTTP_200_OK,
#             data=[]
#         )
#     else:
#         response = success_response(
#             status_code=status.HTTP_200_OK,
#             data=roles
#         )
#     # logger.info(f"{[role.to_dict() for role in roles]}")
#     return response


# Admin Router
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)
@admin_router.get("/", tags=["auth"])
async def admin_dashboard():
    """Admin dashboard endpoint"""
    return {"message": "Admin Dashboard"}
