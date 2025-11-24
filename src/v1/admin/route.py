from fastapi import APIRouter, Depends, status
from .service import SuperAdminService, AdminService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from .schema import CreatePermission, CreateRole, ValidatePermissions
from src.utils.response import success_response
from src.utils.log import setup_logger
logger = setup_logger(__name__, file_path="admin.log")



def get_admin_service(db: AsyncSession = Depends(get_session)):
    return AdminService(db=db)

def get_super_admin_service(db: AsyncSession = Depends(get_session)):
    return SuperAdminService(db=db)


# Super Admin Router
super_admin_router = APIRouter(
    prefix="/super-admin",
    tags=["super-admin"]
)


#routes
@super_admin_router.get("/", tags=["auth"])
async def super_admin_dashboard():
    """Super admin dashboard endpoint"""
    return {"message": "Super Admin Dashboard"}


@super_admin_router.get("/permission")
async def fetch_all_permission(super_admin_service:SuperAdminService = Depends(get_super_admin_service)):
    permission = await super_admin_service.fetch_all_permission() 
    return permission


@super_admin_router.post("/create-role")
#auth decorator here
async def create_role(data:CreateRole,
super_admin_service:SuperAdminService = Depends(get_super_admin_service)
):
    new_role =  await super_admin_service.create_roles(data)
    response = success_response(
        status_code=status.HTTP_201_CREATED,
        data = new_role.to_dict()
    )
    return response

@super_admin_router.get("/fetch-role")
#auth decorator here
async def fetch_all_roles(
super_admin_service:SuperAdminService = Depends(get_super_admin_service)
):
    roles =  await super_admin_service.fetch_all_roles()
    if not roles:
        response = success_response(
            status_code=status.HTTP_200_OK,
            data=[]
        )
    else:
        response = success_response(
            status_code=status.HTTP_200_OK,
            data=roles
        )
    # logger.info(f"{[role.to_dict() for role in roles]}")
    return response


# Admin Router
admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)
@admin_router.get("/", tags=["auth"])
async def admin_dashboard():
    """Admin dashboard endpoint"""
    return {"message": "Admin Dashboard"}