from datetime import datetime, timedelta, timezone
import aiohttp
from typing import Dict, Any
from src.utils.config import config
from src.utils.http_config import http_client
import json
from src.utils.log import setup_logger
from src.v1.base.exception import (
    DSpaceError
)
logger = setup_logger(__name__, "client.log")


class Client:
    """This module handles making requests to DSpace to access its infrastructure"""

    def __init__(self):
        logger.info("Initializing DSpace client")
        self.base_url = config.base_url
        logger.debug(f"Base URL configured as: {self.base_url}")

    async def _make_request(
        self,
        http_method: str,
        req_headers: Dict,
        endpoint: str,
        # params: Dict = None,
        data: Dict = None,
        # cookie_data: Dict = None,
        token: str = None,
        # xrsf_token:str=None 
    ) -> Dict[str, Any]:
        """Make HTTP request to DSpace API"""

        self.session = await http_client.get_session()
        url = f"{self.base_url}{endpoint}"
        http_method = http_method.upper()

        # ================= HEADER HANDLING =================
        headers = {**req_headers} if req_headers else {}
        headers.setdefault("Content-Type", "application/json")


            
        # Optional token (jwt for authentication)
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # ================= REQUEST DATA =================
        request_kwargs = {
            "method": http_method,
            "url": url,
            "headers": headers,
            # "params": params,
        }

        # Handle content type
        content_type = headers.get("Content-Type", "").lower()
        if http_method in ("POST", "PUT", "PATCH"):
            if content_type == "application/x-www-form-urlencoded":
                request_kwargs["data"] = data
            else:
                request_kwargs["json"] = data

        # Optional cookies
        # if cookie_data:
        #     request_kwargs["cookies"] = cookie_data automatic parsing of cookies by aiohttp

        logger.info(f"Making {http_method} request to: {url}")
        logger.debug(f"Request headers: {headers}")
        # logger.debug(f"Request params: {params}")
        logger.debug(f"Request argument: {request_kwargs}")
        # logger.debug(f"Request cookies: {request_kwargs.get("cookies")}")


        try:
            async with self.session.request(**request_kwargs) as response:
                response_headers = response.headers
                return await self._handle_response(response, response_headers)

        except aiohttp.ClientResponseError as e:
            logger.error(
                f"API request failed: Status={e.status}, Message={e.message}, "
                f"URL={e.request_info.real_url}",
                exc_info=True
            )
            raise DSpaceError()

        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}", exc_info=True)
            raise DSpaceError()



    # ================= Helper Method =================
    async def _handle_response(self, response: aiohttp.ClientResponse, headers: Dict[str, Any]):
        """
        Handle the response, raising clean errors when status is not OK.
        """
        logger.debug(f"response headers: {headers}")
        try:
            response.raise_for_status()
            try:
                response_json = await response.json()
                logger.debug(f"Response JSON: {response_json}")
                return response_json, headers
            except aiohttp.ContentTypeError:
                response_text = await response.text()
                logger.warning(f"Non-JSON response received: {response_text}")
                return response_text, headers

        except aiohttp.ClientResponseError as e:
            # Try to extract error body
            error_details = None
            try:
                raw_body = await response.text()
                try:
                    error_details = json.loads(raw_body)
                except json.JSONDecodeError:
                    error_details = raw_body
            except Exception:
                error_details = None

            # Log everything clearly
            logger.error(
                f"Request failed — Status: {e.status}, Message: {e.message or 'Unknown'}, "
                f"URL: {e.request_info.real_url}, Body: {error_details}",
                exc_info=True
            )

            # Raise structured error
            raise DSpaceError()
 
        
    async def get_csrf_token(self):
        logger.info("Requesting CSRF token")
        endpoint = "security/csrf"
        
        headers = {
            "Content-Type": "application/json",
        }
        try:
            response, res_headers = await self._make_request(
                http_method="get",
                endpoint=endpoint,
                req_headers=headers, 
            )
            
            logger.info("CSRF token retrieved successfully")
            cookies = self.session.cookie_jar.filter_cookies(self.base_url)
            cookie_value = list(cookies.values())[0].value
            self.csrf_token = res_headers.get("DSPACE-XSRF-TOKEN")
            if not self.csrf_token:
                logger.error("CSRF token not found in response headers")
                raise DSpaceError("CSRF token not found in response headers")
            logger.debug(f"cookie value: {cookie_value}")
            session_data = {
            "auth_cookie": self.csrf_token,
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        }
            return session_data
        
        except Exception as e:
            logger.error(f"Failed to get CSRF token: {str(e)}", exc_info=True)
            raise DSpaceError()
    
    

dspace_client = Client()