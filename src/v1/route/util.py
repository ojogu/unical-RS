from fastapi import Depends
from src.v1.admin.service import AdminService
from src.v1.admin.permission_service import PermissionService
from src.v1.auth.service import AccessTokenBearer
from src.v1.dspace.service import DspaceAuthService, DspaceGroupService
from src.v1.service.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.db import get_session


async def get_dspace_auth_service():
    return DspaceAuthService()

async def get_dspace_group_service(dspace_auth_service = Depends(get_dspace_auth_service)):
    return DspaceGroupService(dspace_auth_service)


async def get_user_service(db: AsyncSession = Depends(get_session), dspace_auth_service = Depends(get_dspace_auth_service)):
    return UserService(db=db, dspace_auth_service=dspace_auth_service)

async def get_current_user(user_details:dict = Depends(AccessTokenBearer()),
user_service: UserService = Depends(get_user_service)
):
    user_id = user_details["user"]["user_id"]
    user = await user_service.check_if_user_exist_by_id(user_id)
    return user

def get_admin_service(db: AsyncSession = Depends(get_session)):
    return AdminService(db=db)

# def get_super_admin_service(db: AsyncSession = Depends(get_session)):
#     return SuperAdminService(db=db)

def get_permission_service(db: AsyncSession = Depends(get_session)):
    return PermissionService(db=db)
