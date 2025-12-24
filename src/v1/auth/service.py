from datetime import datetime, timedelta
import uuid
from passlib.context import CryptContext
from fastapi import Depends, Request
import jwt
from src.utils.config import config
from src.v1.base.exception import TokenExpired
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.v1.base.exception import InvalidToken
from .schema import Token
from src.utils.redis_client import key_exist, set_cache
from src.utils.log import setup_logger
logger = setup_logger(__name__, "auth_service.log")

ctx = CryptContext(
    schemes=["bcrypt"]
)

def password_hash(password:str)->str:
    hash = ctx.hash(password)
    return hash 


def verify_password(password, password_hash):
    is_valid = ctx.verify(password, password_hash)
    return is_valid 

class AuthService():
    """this class handles in-app authentication (jwt access token, refresh token)
    """
    
    def __init__(self):
        pass
    
    def create_access_token(self, user_data:dict, expiry:timedelta=None, refresh:bool = False):
        try:
            # payload["user"] = user_data
            # payload["exp"] = datetime.now() + to_expire
            # payload["jti"] = str(uuid.uuid4())
            # payload["refresh"] = refresh
            
            to_expire = timedelta(seconds=expiry) if expiry is not None else timedelta(seconds=config.access_token_expiry)
            payload = Token(
                user=user_data,
                exp = datetime.now() + to_expire,
                jti= str(uuid.uuid4()),
                refresh=refresh 
            ).model_dump()
            
            token = jwt.encode(
                payload=payload,
                key=config.jwt_secret_key,
                algorithm=config.jwt_algo
            )
            logger.info(f"token created for user: {user_data.get('id')}")
            return token
        except Exception as e:
            logger.error(f"error creating access token for user {user_data.get('id')}: {e}", exc_info=True)
            raise
    
    def decode_token(self, token:str)-> dict:
        try:
            token_data = jwt.decode(
                jwt=token,
                key=config.jwt_secret_key,
                algorithms=[config.jwt_algo]
            )
            logger.info(f"token decoded successfully for user: {token_data.get('user').get('id')}")
            return token_data
        except jwt.ExpiredSignatureError as e:
            logger.error(f"token expired for user: {e}", exc_info=True)
            raise TokenExpired("token has expired")
        
        except jwt.InvalidSignatureError as e:
            logger.error(f"invalid token signature: {e}", exc_info=True)
            raise TokenExpired("invalid token signature")
        
        except jwt.PyJWTError as e:
            logger.error(f"error decoding token: {e}", exc_info=True)
            raise TokenExpired("error decoding token")

auth_service = AuthService()



class TokenService(HTTPBearer):
    """
        Custom HTTP Bearer authentication class for validating JWT access tokens.

        This class extends FastAPI's HTTPBearer to:
        - Extract Bearer tokens from the Authorization header.
        - Decode and validate the token using an external `auth_service`.
        - Ensure the token is not a refresh token.
        - Raise a custom `InvalidToken` exception if the token is invalid or missing required data.

        Usage:
            Use as a dependency in FastAPI routes to protect endpoints and extract token data.

        Example:
            access_token_service = AccessTokenService()

            @router.get("/secure-endpoint")
            async def secure_endpoint(user_data: dict = Depends(access_token_service)):
                return {"user": user_data}

        Args:
            auto_error (bool): Whether to automatically raise an HTTPException
                if authentication fails. Defaults to True.

        Raises:
            InvalidToken: If the token is missing, invalid, expired, or is a refresh token.
        """

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        # Step 1: Extract token from Authorization header
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if not credentials or not credentials.scheme.lower() == "bearer":
            raise InvalidToken("Invalid authentication scheme")

        token = credentials.credentials

        # Step 2: Validate token
        # if not self.token_valid(token):
        #     raise InvalidToken("Invalid or expired token")

        # Step 3: Decode token
        try:
            token_data = auth_service.decode_token(token)
        except Exception as e:
            logger.error(f"an error occurred during decoding token: {e}")
            raise InvalidToken("Invalid or expired token")

        if not token_data:
            raise InvalidToken("No data found in token")

        #check if token in  blacklist 
        if await key_exist(key=token_data["jti"]):
            raise InvalidToken("Token has been revoked, get new token") 
        # Allow child to validate token type (access or refresh)
        self.verify_token_type(token_data)
        
        return token_data


    def verify_token_type(self, token_data:dict):
        raise NotImplementedError("Overide in the child classes ")

class AccessTokenBearer(TokenService):
    def verify_token_type(self, token_data:dict):
        """
        Verifies that the token data is a valid access token.

        Args:
            token_data (dict): The decoded token data.

        Raises:
            InvalidToken: If the token is a refresh token.
        """
        if token_data and token_data.get("refresh", False):
            raise InvalidToken("Please provide a valid access token, not a refresh token")
        
class RefreshTokenBearer(TokenService):
    def verify_token_type(self, token_data:dict):
        """
        Verifies that the token data is a valid refresh token.

        Args:
            token_data (dict): The decoded token data.

        Raises:
            InvalidToken: If the token is an access token.
        """
        if token_data and not token_data.get("refresh", False):
            raise InvalidToken("Please provide a valid refresh token")



    