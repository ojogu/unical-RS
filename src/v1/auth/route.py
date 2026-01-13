from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from src.utils.redis_client import set_cache, key_exist
from src.v1.auth.service import AccessTokenBearer, RefreshTokenBearer, auth_service
from src.v1.auth.schema import CreateUser, Login
from src.utils.response import success_response
from src.utils.log import setup_logger
from src.v1.route.util import get_user_service
from src.v1.service.user_service import UserService
from src.v1.model.roles import Role_Enum
from src.v1.base.exception import InvalidToken
logger = setup_logger(__name__, "auth_route.log")

# auth for users
auth_router = APIRouter(prefix="/auth", tags=["user"])

@auth_router.post("/login", tags=["auth"])
async def login(login_data: Login, user_service: UserService = Depends(get_user_service)):
    """Shared login endpoint for all user types."""
    user_data = await user_service.authenticate_user(login_data)
    access_token = auth_service.create_access_token(user_data=user_data)
    refresh_token = auth_service.create_access_token(user_data=user_data, refresh=True)
    tokens = {"access_token": access_token, "refresh_token": refresh_token}
    return success_response(message="Login successful", status_code=status.HTTP_200_OK, data=tokens)

@auth_router.post("/register/admin", tags=["auth"])
async def register_admin(user_data: CreateUser, user_service: UserService = Depends(get_user_service)):
    """Registration endpoint for admin users."""
    # Ensure role is admin
    user_data.role = Role_Enum.ADMIN
    await user_service.create_user(user_data)
    return success_response(message="Admin registered successfully", status_code=status.HTTP_201_CREATED)

@auth_router.post("/register/lecturer", tags=["auth"])
async def register_lecturer(user_data: CreateUser, user_service: UserService = Depends(get_user_service)):
    """Registration endpoint for lecturer users."""
    # Ensure role is lecturer
    user_data.role = Role_Enum.LECTURER
    await user_service.create_user(user_data)
    return success_response(message="Lecturer registered successfully", status_code=status.HTTP_201_CREATED)

@auth_router.post("/register/student", tags=["auth"])
async def register_student(user_data: CreateUser, user_service: UserService = Depends(get_user_service)):
    """Registration endpoint for student users."""
    # Ensure role is student
    user_data.role = Role_Enum.STUDENT
    await user_service.create_user(user_data)
    return success_response(message="Student registered successfully", status_code=status.HTTP_201_CREATED)

@auth_router.post("/register", tags=["auth"])
async def register_user(user_data: CreateUser, user_service: UserService = Depends(get_user_service)):
    """Registration endpoint for normal users."""
    # Ensure role is user
    user_data.role = Role_Enum.USER
    await user_service.create_user(user_data)
    return success_response(message="User registered successfully", status_code=status.HTTP_201_CREATED)

@auth_router.get("/refresh-token", tags=["auth"])
async def get_new_tokens_token(token_details:dict = Depends(RefreshTokenBearer())):
    # Check if refresh token is not blacklisted (additional check)
    jti = token_details["jti"]
    if await key_exist(key=str(jti)):
        raise InvalidToken("Refresh token has been revoked")

    # Make sure it's not expired
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        access_token = auth_service.create_access_token(
            user_data=token_details["user"]
        )
        refresh_token = auth_service.create_access_token(
            user_data=token_details["user"],
            refresh=True
        )

        # Blacklist the old refresh token
        await set_cache(
            key=str(jti),
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



@auth_router.get("/logout", tags=["auth"])
async def revoke_token(token_details:dict = Depends(RefreshTokenBearer())):
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
     