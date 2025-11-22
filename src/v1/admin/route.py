from fastapi import APIRouter, Depends
from .service import SuperAdminService, AdminService
from src.utils.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

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
    pass 




# Admin Router
admin_router = APIRouter(
    prefix="admin",
    tags=["admin"]
)
@admin_router.get("/", tags=["auth"])
async def admin_dashboard():
    """Admin dashboard endpoint"""
    return {"message": "Admin Dashboard"}