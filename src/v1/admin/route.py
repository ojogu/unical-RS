#dspace auth routes
from fastapi import APIRouter, HTTPException, status 
from src.v1.dspace.dspace_auth.auth import dspace_auth_service
from src.v1.schema.auth import Register, Login
from src.utils.log import setup_logger

logger = setup_logger(__name__, "dspace_auth_routes.log")

# auth for implement admin endpoints, or use http client to access this
dspace_auth_router = APIRouter(prefix="/admin")

@dspace_auth_router.post("/login")
async def login(data: Login):
    email = data.email
    password = data.password
        
    logger.info(f"Login attempt for user: {email}")
    req_login = await dspace_auth_service.login(email, password)
    logger.info(f"Successful login for user: {email}")
        
    return req_login
        
        # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
