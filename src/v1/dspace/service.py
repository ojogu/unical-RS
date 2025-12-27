from src.v1.dspace.client import DspaceClient
from src.utils.redis_client import set_cache, get_or_fetch_cache, get_from_cache
from src.utils.config import config
from src.v1.auth.schema import Login, CreateUser, EPersonCreate
from src.utils.log import setup_logger
from src.v1.base.exception import (
    BadRequest,
    DSpaceError
)
from src.v1.dspace.schema import CreateGroup
from pydantic import ValidationError
from enum import Enum
from functools import partial
logger = setup_logger(__name__, "dspace_auth_service.log")
logger_group = setup_logger("dspace_group_service", "dspace_group_service.log")

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
        # user = config.base_username
        # password = config.base_password
        # use the super admin cred, this is the cred we'll be using to manipulate dspace, eg able to create other users since dspace requires having an authenticated admin jwt to get token to create users on dspace ends
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
            crsf_token = res_headers.get("DSPACE-XSRF-TOKEN")
            jwt_token = res_headers.get("Authorization")
            token = await self.status(jwt_token, crsf_token)
            logger.info(f"new token: {token}")
            
            data = {
                "DSPACE-XSRF-TOKEN":token,
                "jwt_token": jwt_token 
            }
            await set_cache(email, data)
            logger.info(f"set cache for: {data}")
            return data
            
        except Exception as e:
            logger.error(f"Login failed for user {email}: {str(e)}")
            raise DSpaceError()
    
    async def register(self, user_data: CreateUser):
        try:
            self.login_callback = partial(self.login, config.base_username, config.base_password)
            
            logger.info(f"Attempting to register new user: {user_data.email}")
            
            # base_user = config.base_username
            # base_password = config.base_password
            
            # Make the request with base credentials to fetch tokens for user creation
            
            #check redis for token to reduce API call
            tokens:dict = await get_or_fetch_cache(config.base_username, self.login_callback)
            # tokens: dict = await self.login(base_user, base_password)
            crsf_token = tokens.get("DSPACE-XSRF-TOKEN")
            jwt_token = tokens.get("jwt_token")
            
            if not crsf_token or not jwt_token:
                logger.error("Failed to obtain required tokens for user registration")
                raise BadRequest()
                # raise BadRequest("Failed to obtain authentication tokens")
            
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
    
    async def status(self, access_token, crsf_token):
        try:
            logger.info("Attempting to fetch authentication status")
            headers = {
                "Authorization": access_token,
                "X-XSRF-TOKEN": crsf_token
            }
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.GET,
                endpoint="authn/status",
                req_headers=headers
            )
            logger.info("Authentication status retrieved successfully")
            logger.debug(f"Response headers: {res_headers}")
            logger.debug(f"Response body: {req}")
            token = res_headers.get("DSPACE-XSRF-TOKEN")
            return token
        except Exception as e:
            logger.error(f"Failed to fetch authentication status: {str(e)}")
            raise DSpaceError()




class DspaceGroupService():
    """this class handles group operations for dspace"""
    def __init__(self, auth_service: "DspaceAuthService"):
        self.auth_service = auth_service
        self.login_callback = partial(self.auth_service.login, config.base_username, config.base_password)

    
    async def create_group(self, group_data:CreateGroup):
        try:
            #groups represents roles
            #it will be an atomic operation to when creating roles from our admin endpoints
            logger_group.info(f"group data: {group_data.model_dump()}")
            tokens = await get_or_fetch_cache(config.base_username, self.login_callback)
            crsf_token = tokens.get("DSPACE-XSRF-TOKEN")
            jwt_token = tokens.get("jwt_token")
            header = {
                "X-XSRF-TOKEN": crsf_token
            }
            if not crsf_token or not jwt_token:
                logger_group.error("Failed to obtain required tokens for user registration")
                raise DSpaceError()

            req, res_headers = await dspace_client._make_request(
                    http_method=HTTPMethod.POST,
                    endpoint="eperson/groups",
                    data=group_data.model_dump(exclude={"role_name"}),
                    req_headers = header,
                    jwt_token=jwt_token
                )

            logger_group.info(f"group created successfully: {group_data.name}")
            logger_group.debug(f"Response headers: {res_headers}")
            logger_group.debug(f"Response body: {req}")

            return req
        # except (BadRequest,) as e:
        #     logger_group.error(f"Failed to create group {group_data.name}: {str(e)}")
        #     raise
        except Exception as e:
            logger_group.error(f"Unexpected error during group creation for {group_data.name}: {str(e)}", exc_info=True)
            raise DSpaceError()


    
    async def fetch_single_group(self, group_id:str):
        try:
            logger_group.info(f"Fetching single group with ID: {group_id}")
            req, res_header = await dspace_client._make_request(
                http_method=HTTPMethod.GET,
                endpoint=f"eperson/groups/{group_id}"
            )
            logger_group.info(f"Group fetched successfully: {group_id}")
            logger_group.debug(f"Response headers: {res_header}")
            logger_group.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger_group.error(f"Failed to fetch group with ID {group_id}: {str(e)}")
            raise DSpaceError()
    
    async def search_group_by_name(self, query):
        try:
            logger_group.info(f"Searching for group with query: {query}")
            
            #make request
            req, res_header = await dspace_client._make_request(
                http_method=HTTPMethod.GET,
                endpoint="eperson/groups/search/byMetadata",
                query_params=query
            )
            logger_group.info("Group search completed successfully")
            logger_group.debug(f"Response headers: {res_header}")
            logger_group.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger_group.error(f"Failed to search group with query {query}: {str(e)}")
            raise DSpaceError()

    async def delete_group(self, group_id):
        try:
            logger_group.info(f"Attempting to delete group with ID: {group_id}")
            #fetch tokens
            tokens = await get_or_fetch_cache(config.base_username, self.login_callback)
            crsf_token = tokens.get("DSPACE-XSRF-TOKEN")
            jwt_token = tokens.get("jwt_token")

            if not crsf_token or not jwt_token:
                logger_group.error("Failed to obtain required tokens for group deletion")
                raise DSpaceError()

            #make request
            req, res_headers = await dspace_client._make_request(
                endpoint=f"eperson/groups/{group_id}",
                http_method=HTTPMethod.DELETE,
                jwt_token=jwt_token

            )
            logger_group.info(f"Group deleted successfully: {group_id}")
            logger_group.debug(f"Response headers: {res_headers}")
            logger_group.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger_group.error(f"Failed to delete group {group_id}: {str(e)}")
            raise DSpaceError()
        
        
    async def update_group_name(self, group_id, new_name):
        try:
            logger_group.info(f"Attempting to update group name for group ID: {group_id}")
            # Fetch tokens
            tokens = await get_or_fetch_cache(config.base_username, self.login_callback)
            crsf_token = tokens.get("DSPACE-XSRF-TOKEN")
            jwt_token = tokens.get("jwt_token")

            if not crsf_token or not jwt_token:
                logger_group.error("Failed to obtain required tokens for group name update")
                raise DSpaceError()

            # Prepare JSON patch data
            patch_data = [
                {
                    "op": "replace",
                    "path": "/name",
                    "value": new_name
                }
            ]

            # Make PATCH request
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.PATCH,
                endpoint=f"eperson/groups/{group_id}",
                data=patch_data,
                jwt_token=jwt_token
            )

            logger_group.info(f"Group name updated successfully for group ID: {group_id}")
            logger_group.debug(f"Response headers: {res_headers}")
            logger_group.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger_group.error(f"Failed to update group name for group ID {group_id}: {str(e)}")
            raise DSpaceError()
    
    async def update_metadata(group_id):
        #update meta data and group name (PATCH)
        endpoint:str = f"eperson/groups/{group_id}"
        pass 
    
    async def fetch_users_in_a_group(self, group_id):
        try:
            logger_group.info(f"Fetching users in group with ID: {group_id}")
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.GET,
                endpoint=f"eperson/groups/{group_id}/epersons"
            )
            logger_group.info(f"Users in group fetched successfully: {group_id}")
            logger_group.debug(f"Response headers: {res_headers}")
            logger_group.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger_group.error(f"Failed to fetch users in group with ID {group_id}: {str(e)}")
            raise DSpaceError()
    
    async def link_user_to_group(self, user_id, group_id):
        try:
            logger_group.info(f"Attempting to link user {user_id} to group {group_id}")
            # Fetch tokens
            tokens = await get_or_fetch_cache(config.base_username, self.login_callback)
            crsf_token = tokens.get("DSPACE-XSRF-TOKEN")
            jwt_token = tokens.get("jwt_token")

            if not crsf_token or not jwt_token:
                logger_group.error("Failed to obtain required tokens for linking user to group")
                raise DSpaceError()

            # Prepare user URI
            user_uri = f"{config.base_url}/eperson/epersons/{user_id}"

            # Make POST request with text/uri-list content type
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.POST,
                endpoint=f"eperson/groups/{group_id}/epersons",
                data=user_uri,
                req_headers={"Content-Type": "text/uri-list"},
                jwt_token=jwt_token
            )

            logger_group.info(f"User {user_id} linked to group {group_id} successfully")
            logger_group.debug(f"Response headers: {res_headers}")
            logger_group.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger_group.error(f"Failed to link user {user_id} to group {group_id}: {str(e)}")
            raise DSpaceError()
    
    async def change_users_in_a_group(group_id):
        endpoint:str = f"eperson/groups/{group_id}/epersons" #PUT request
        
    async def remove_user_in_a_group(self, group_id, user_id):
        try:
            logger_group.info(f"Attempting to remove user {user_id} from group {group_id}")
            # Fetch tokens
            tokens = await get_or_fetch_cache(config.base_username, self.login_callback)
            crsf_token = tokens.get("DSPACE-XSRF-TOKEN")
            jwt_token = tokens.get("jwt_token")

            if not crsf_token or not jwt_token:
                logger_group.error("Failed to obtain required tokens for removing user from group")
                raise DSpaceError()

            # Make DELETE request
            req, res_headers = await dspace_client._make_request(
                http_method=HTTPMethod.DELETE,
                endpoint=f"eperson/groups/{group_id}/epersons/{user_id}",
                jwt_token=jwt_token
            )

            logger_group.info(f"User {user_id} removed from group {group_id} successfully")
            logger_group.debug(f"Response headers: {res_headers}")
            logger_group.debug(f"Response body: {req}")
            return req
        except Exception as e:
            logger_group.error(f"Failed to remove user {user_id} from group {group_id}: {str(e)}")
            raise DSpaceError()
    
class SubGroup():
    def __init__(self, group_service: "DspaceGroupService"):
        self.group_service = group_service
    
    
    




dspace_auth_service = DspaceAuthService()
dspace_group_service = DspaceGroupService(dspace_auth_service)
