from fastapi import APIRouter, HTTPException, status
from src.v1.dspace.client import dspace_client

# auth for users
user_auth_router = APIRouter(prefix="/lims", tags=["user"])

@user_auth_router.post("/login", tags=["auth"])
async def login():
    pass 

