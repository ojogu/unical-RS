import aiohttp
from typing import Dict, Any
from src.utils.config import config
from src.utils.http_config import http_client
import json
from src.utils.log import setup_logger
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
        params: Dict = None,
        data: Dict = None,
        cookie_data: Dict = None,
    ) -> Dict[str, Any]:
        
        """Make HTTP request to DSpace API"""

        self.session = await http_client.get_session()
        url = f"{self.base_url}{endpoint}"

        logger.info(f"Making {http_method.upper()} request to: {url}")
        logger.debug(f"Request parameters: {params}")
        logger.debug(f"Request headers: {req_headers}")

        try:
            # ================= GET =================
            if http_method.upper() == 'GET':
                async with self.session.get(url, headers=req_headers, params=params) as response:
                    headers = response.headers
                    return await self._handle_response(response, headers)

            # ================= POST =================
            elif http_method.upper() == 'POST':
                content_type = req_headers.get("Content-Type", "").lower()
                if content_type == "application/x-www-form-urlencoded":
                    async with self.session.post(
                        url, headers=req_headers, params=params, data=data
                    ) as response:
                        return await self._handle_response(response, response.headers)
                else:
                    async with self.session.post(
                        url, headers=req_headers, params=params, json=data
                    ) as response:
                        return await self._handle_response(response, response.headers)

            # ================= DELETE =================
            elif http_method.upper() == 'DELETE':
                async with self.session.delete(url, headers=req_headers, params=params) as response:
                    return await self._handle_response(response, response.headers)

        except aiohttp.ClientResponseError as e:
            logger.error(
                f"API request failed: Status={e.status}, Message={e.message}, "
                f"URL={e.request_info.real_url}",
                exc_info=True
            )
            raise

        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}", exc_info=True)
            raise



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
            raise Exception({
                "status": e.status,
                "url": str(e.request_info.real_url),
                "message": e.message or "HTTP Error",
                "details": error_details
            }) from e
 
        
        
        
    async def get_csrf_token(self):
        logger.info("Requesting CSRF token")
        endpoint = "security/csrf"
        
        cookies = self.session.cookie_jar.filter_cookies(self.base_url)
        cookie_dict = {c.key: c.value for c in cookies.values()}
        headers = {
            "Content-Type": "application/json",
        }
        try:
            response, res_headers = await self._make_request(
                http_method="get",
                endpoint=endpoint,
                req_headers=headers
            )
            
            logger.info("CSRF token retrieved successfully")
            self.csrf_token = res_headers.get("DSPACE-XSRF-TOKEN")
            if not self.csrf_token:
                raise Exception("CSRF token not found in response headers")

            return self.csrf_token
        except Exception as e:
            logger.error(f"Failed to get CSRF token: {str(e)}", exc_info=True)
            raise
    
    

dspace_client = Client()