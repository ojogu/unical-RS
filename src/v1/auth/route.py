from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from src.utils.redis_client import set_cache
from src.v1.auth.service import AccessTokenBearer, RefreshTokenBearer, auth_service
from src.v1.auth.schema import CreateUser
from src.v1.dspace.client import dspace_client
from src.utils.response import success_response
from src.utils.log import setup_logger

logger = setup_logger(__name__, "auth_route.log")

# auth for users
auth_router = APIRouter(prefix="/auth", tags=["user"])

@auth_router.post("/login", tags=["auth"])
async def login():
    pass 

@auth_router.post("/register", tags=["auth"])
async def register(user_data: CreateUser):
    pass 

@auth_router.get("/refresh-token")
async def get_new_tokens_token(token_details:dict = Depends(RefreshTokenBearer())):
    #make sure it's not expired
    expiry_timestamp = token_details["exp"] 
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        access_token = auth_service.create_access_token(
            user_data=token_details["user"]
        )
        refresh_token = auth_service.create_access_token(
            user_data=token_details["user"],
            refresh=True
        )
        
        #blacklist the refresh token 
        jti = token_details["jti"]
        await set_cache(
            key= str(jti),
            data=""
        )
        logger.info(f"{jti} has been revoked")
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        
        return success_response(
        message="Refresh Token Successfully Generated",
        status_code=status.HTTP_200_OK,
        data=tokens
    )



@auth_router.get("/logout")
async def revoke_token(token_details:dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await set_cache(
        key= str(jti),
        data=""
    )
    return success_response(
        message="Logged Out Successfully",
        status_code=status.HTTP_200_OK,
        data=None
    )
     