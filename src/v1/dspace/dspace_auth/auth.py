from src.v1.dspace.client import dspace_client
from src.utils.redis import get_redis, get_or_fetch_cache
from src.v1.schema.auth import Register, Login
from src.utils.log import setup_logger
from src.v1.base.exception import (
    BadRequest,
    DSpaceError
)
from pydantic import ValidationError

logger = setup_logger(__name__, "dspace_auth_service.log")

class DspaceAuthService():
    """this class handles authentication and authorization for dspace"""
    def __init__(self):
        pass
    
    async def login(self, email: str, password: str):
        try:
            logger.info(f"Attempting login for user: {email}")
            token:dict = await self._fetch_csrf_token(email)
            xsrf_token = token.get("auth_cookie")
            headers = {
                "X-XSRF-TOKEN": xsrf_token,
                "Content-Type": "application/x-www-form-urlencoded",
            }
            #package cookie
            cookie = {
                "DSPACE-XSRF-COOKIE": xsrf_token
            }
            
            payload = {
                "email": email,
                "password": password
            }
            logger.info(f"payload: {payload}")
            try:
                validated_data = Login(**payload).model_dump()
            except ValidationError as e:
                logger.error(f"Validation error for login payload: {str(e)}")
                raise 
            
            # Rename "email" to "user"
            validated_data["user"] = validated_data.pop("email")
            logger.info(f"validated data: {validated_data}")
            req = await dspace_client._make_request(
                http_method="post",
                endpoint="authn/login",
                data=validated_data,
                req_headers=headers,
                # cookie_data=cookie
            )
            logger.info(f"Login successful for user: {email}")
            return req
            
        except Exception as e:
            logger.error(f"Login failed for user {email}: {str(e)}")
            raise DSpaceError()
    
    def register(self):
        logger.warning("Register method not implemented")
        pass
    
    @staticmethod
    async def _fetch_csrf_token(email: str):
        try:
            token = await get_or_fetch_cache(str(email), dspace_client.get_csrf_token)
            logger.debug(f"CSRF token fetched for {email}. Token:{token}")
            return token
        except Exception as e:
            logger.error(f"Failed to fetch CSRF token for {email}: {str(e)}")
            raise
    
    async def refresh_token(self):
        logger.warning("Refresh token method not implemented")
        pass 

dspace_auth_service = DspaceAuthService()


