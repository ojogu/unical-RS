from src.v1.dspace.client import DspaceClient
from src.utils.redis_client import set_cache, get_or_fetch_cache
from src.utils.config import config
from src.v1.auth.schema import Login, CreateUser, EPersonCreate
from src.utils.log import setup_logger
from src.v1.base.exception import (
    BadRequest,
    DSpaceError
)
from pydantic import ValidationError
from enum import Enum

logger = setup_logger(__name__, "dspace_auth_service.log")

class HTTPMethod(str, Enum):
    """Enum for HTTP verbs"""
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    HEAD = "head"
    OPTIONS = "options"

dspace_client = DspaceClient()

class DspaceAuthService():
    """this class handles authentication and authorization for dspace"""
    def __init__(self):
        pass
    
    async def login(self, email: str, password: str):
        try:
            
            logger.info(f"Attempting login for user: {email}")
            #fetch a new token for every login 
            token = await dspace_client.get_csrf_token()
            # token:dict = await self._fetch_csrf_token(email)
            
            xsrf_token = token.get("DSPACE-XSRF-TOKEN")
            headers = {
                "X-XSRF-TOKEN": xsrf_token,
                "Content-Type": "application/x-www-form-urlencoded",
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
            
            #well have a retry mechanism 
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.POST,
                endpoint="authn/login",
                data=validated_data,
                req_headers=headers,
                # cookie_data=cookie
            )
            logger.info(f"Login successful for user: {email}")
            logger.debug(f"headers: {res_headers}")
            logger.debug(f"res body: {req}")
            
            #update jwt/header token to from header, so can access for other endpoints
            new_token = res_headers.get("DSPACE-XSRF-TOKEN")
            jwt_token = res_headers.get("Authorization")
            data = {
                "DSPACE-XSRF-TOKEN":new_token,
                "jwt_token": jwt_token 
            }
            await set_cache(email, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Login failed for user {email}: {str(e)}")
            raise DSpaceError()
    
    async def register(self, user_data: CreateUser):
        try:
            logger.info(f"Attempting to register new user: {user_data.email}")
            
            base_user = config.base_username
            base_password = config.base_password
            
            # Make the request with base credentials to fetch tokens for user creation
            tokens: dict = await self.login(base_user, base_password)
            crsf_token = tokens.get("DSPACE-XSRF-TOKEN")
            jwt_token = tokens.get("jwt_token")
            
            if not crsf_token or not jwt_token:
                logger.error("Failed to obtain required tokens for user registration")
                raise BadRequest("Failed to obtain authentication tokens")
            
            logger.debug("Tokens obtained for user registration")
            
            # Prepare data for dspace
            new_user = EPersonCreate(
                name=user_data.user_name,
                email=user_data.email,
                metadata={
                    "eperson.firstname": [{"value": user_data.first_name}],
                    "eperson.lastname": [{"value": user_data.last_name}]
                }
            ).model_dump_json()
            
            # Make request to dspace register endpoint
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.POST,
                endpoint="eperson/epersons",
                data=new_user,
                jwt_token=jwt_token
            )
            
            logger.info(f"User registered successfully: {user_data.email}")
            logger.debug(f"Response headers: {res_headers}")
            logger.debug(f"Response body: {req}")
            
            return req
            
        except (BadRequest, ValidationError) as e:
            logger.error(f"Registration failed for user {user_data.email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during registration for user {user_data.email}: {str(e)}")
            raise DSpaceError()
        
    

    #fetch token from login in which we'll use to register.     
    @staticmethod
    async def _fetch_csrf_token(email: str):
        #this methods fetches token from the cache, or make a request to get a new one
        try:
            token = await get_or_fetch_cache(str(email), dspace_client.get_csrf_token)
            logger.debug(f"CSRF token fetched for {email}. Token:{token}")
            return token
        except Exception as e:
            logger.error(f"Failed to fetch CSRF token for {email}: {str(e)}")
            raise DSpaceError()
    
    async def refresh_token(self, access_token):
        try:
            logger.info("Attempting to refresh token")
            headers = {
                "Authorization": access_token
            }
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.POST,
                endpoint="authn/login",
                req_headers=headers,
            )
            logger.info("Token refreshed successfully")
            logger.debug(f"Response headers: {res_headers}")
            logger.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise DSpaceError()


    async def logout(self, access_token):
        try:
            logger.info("Attempting to logout")
            headers = {
                "Authorization": access_token
            }
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.POST,
                endpoint="authn/logout",
                req_headers=headers,
            )
            logger.info("Logout successful")
            logger.debug(f"Response headers: {res_headers}")
            logger.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger.error(f"Failed to logout: {str(e)}")
            raise DSpaceError()
    
    async def status(self, access_token):
        try:
            logger.info("Attempting to fetch authentication status")
            headers = {
                "Authorization": access_token
            }
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.GET,
                endpoint="authn/status",
                req_headers=headers
            )
            logger.info("Authentication status retrieved successfully")
            logger.debug(f"Response headers: {res_headers}")
            logger.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger.error(f"Failed to fetch authentication status: {str(e)}")
            raise DSpaceError()
 
dspace_auth_service = DspaceAuthService()


