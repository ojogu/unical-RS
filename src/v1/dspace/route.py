# dspace auth routes
from fastapi import APIRouter, Depends

from src.utils.log import setup_logger
from src.v1.dspace.schema import CreateGroup
from src.v1.dspace.service import DspaceAuthService, DspaceGroupService
from src.v1.auth.schema import CreateUser, Login

logger = setup_logger(__name__, "dspace_auth_routes.log")

# auth for implement admin endpoints for testing, or use http client to access this
dspace_auth_router = APIRouter(prefix="/dspace", tags=["DSpace"])

async def get_auth_service():
    return DspaceAuthService()

async def get_group_service(auth_service = Depends(get_auth_service)):
    return DspaceGroupService(auth_service)

@dspace_auth_router.post("/login", tags=["auth"])
async def login(data: Login, auth_service:DspaceAuthService = Depends(get_auth_service)):
    email = data.email
    password = data.password

    logger.info(f"Login attempt for user: {email}")
    req_login = await auth_service.login(email, password)
    logger.info(f"Successful login for user: {email}")

    return req_login


@dspace_auth_router.post("/register", tags=["auth"])
async def register(data: CreateUser):
    # in a normal flow, only already existing admin can register new users, so before trying to create a new user, we'll authenticate with our super admin details, and grab the auth tokens, which would enable us create user

    # super admin creates admins and other admin roles like libarians etc
    pass


@dspace_auth_router.post("/status", tags=["auth"])
# use our in app jwt
async def auth_status():
    pass

@dspace_auth_router.post("/groups", tags=["auth"])
# use our in app jwt
async def create_group(
    group_data:CreateGroup,
    group_service: DspaceGroupService = Depends(get_group_service)):
    pass


