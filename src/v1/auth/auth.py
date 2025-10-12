from fastapi import APIRouter, HTTPException, status
from src.v1.dspace.client import dspace_client

# auth for users
auth_router = APIRouter(prefix="/lims")

@auth_router.post("/login")
async def login():
    pass 

