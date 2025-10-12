
from typing import Any, Callable, Dict
from fastapi import FastAPI, Request, HTTPException, status
from src.v1.base.schema import ErrorResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.v1.base.exception import (
    Environment_Variable_Exception,
    InUseError,
    TokenExpired,
    InvalidToken,
    NotFoundError,
    AlreadyExistsError,
    InvalidEmailPassword,
    BadRequest,
    NotVerified,
    EmailVerificationError,
    DatabaseError,
    ServerError,
    NotActive, 
    BaseExceptionClass
    
    
)
from src.utils.log import setup_logger
exception_logger = setup_logger(__name__, file_path="error.log")




def create_exception_handler(
    status_code: int, initial_detail: Dict
) -> Callable[[Request, Exception], JSONResponse]:
    """Create a standardized exception handler"""
    
    async def exception_handler(request: Request, exc: BaseExceptionClass):
        # Log the exception details
        exception_logger.error(f"Exception occurred: {str(exc)}")

        # Copy initial detail and override the message dynamically
        response_payload = initial_detail.copy()
        if hasattr(exc, "message"):
            response_payload["message"] = str(exc.message)

        # Validate the response payload using ErrorResponse schema
        validated_data = ErrorResponse(**response_payload)
        return JSONResponse(
            content=validated_data.model_dump(), status_code=status_code
        )

    return exception_handler


def register_error_handlers(app: FastAPI):
    """Register all exception handlers for the FastAPI app"""
    
    # Custom exception handlers
    app.add_exception_handler(
        Environment_Variable_Exception,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "status": "error",
                "message": "Environment variable missing",
                "error_code": "environment_variable_missing",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        InUseError,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "status": "error",
                "message": "Resource already in use",
                "error_code": "resource_in_use",
                "data": None,
                "role": None
            }
        )
    )
    
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "status": "error",
                "message": "Invalid token",
                "error_code": "access or refresh token invalid",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        TokenExpired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "status": "error",
                "message": "Token expired",
                "error_code": "token_expired",
                "resolution": "Please get a new token",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        NotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "status": "error",
                "message": "Resource not found",
                "error_code": "not_found",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        AlreadyExistsError,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "status": "error",
                "message": "Resource already exists",
                "error_code": "already_exists",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        InvalidEmailPassword,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "status": "error",
                "message": "Invalid email or password",
                "error_code": "invalid_credentials",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        BadRequest,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "status": "error",
                "message": "Bad request",
                "error_code": "bad_request",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        NotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "status": "error",
                "message": "Account not verified",
                "error_code": "not_verified",
                "resolution": "Please verify your account",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        EmailVerificationError,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "status": "error",
                "message": "Email verification failed",
                "error_code": "email_verification_failed",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        DatabaseError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "status": "error",
                "message": "Database error occurred",
                "error_code": "database_error",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        ServerError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "status": "error",
                "message": "Internal server error",
                "error_code": "server_error",
                "data": None,
                "role": None
            }
        )
    )

    app.add_exception_handler(
        NotActive,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "status": "error",
                "message": "Account is not active",
                "error_code": "account_not_active",
                "resolution": "Please activate your account",
                "data": None,
                "role": None
            }
        )
    )

    # Built-in exception handlers
    app.add_exception_handler(
        HTTPException,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,  # Default, will be overridden
            initial_detail={
                "status": "error",
                "message": "HTTP error occurred",
                "error_code": "http_error",
                "data": None,
                "role": None
            }
        )
    )


    """
    general exception handlers
    """
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        exception_logger.error(f"HTTP {exc.status_code}: {exc.detail}")
        return JSONResponse(
            content={
                "status": "error",
                "message": exc.detail,
                "error_code": "http_error",
                "data": None,
                "role": None
            },
            status_code=exc.status_code
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        error_details = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_details.append(f"{field}: {message}")
        
        error_message = "; ".join(error_details)
        exception_logger.error(f"Validation error: {error_message}")
        
        return JSONResponse(
            content={
                "status": "error",
                "message": error_message,
                "error_code": "validation_error",
                "data": exc.errors(),
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        exception_logger.error(f"Pydantic validation error: {str(exc)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": "Validation error",
                "error_code": "pydantic_validation_error",
                "data": exc.json(),
                "model": exc.model.__name__ 
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        exception_logger.error(f"Integrity error: {str(exc)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": "Integrity error: An object with this value already exists",
                "error_code": "integrity_error",
                "data": None,
                "role": None
            },
            status_code=status.HTTP_409_CONFLICT
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        exception_logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": "Database error",
                "error_code": "database_error",
                "data": None,
                "role": None
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # @app.exception_handler(500)
    # async def internal_server_error(request: Request, exc: Exception):
    #     exception_logger.error(f"Internal server error: {str(exc)}")
    #     return JSONResponse(
    #         content={
    #             "status": "error",
    #             "message": "Oops! Something went wrong",
    #             "error_code": "server_error",
    #             "data": None,
    #             "role": None
    #         },
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    #     )

    # # General exception handler (catch-all)
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        exception_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            content={
                "status": "error",
                "message": "An unexpected error occurred",
                "error_code": "unexpected_error",
                "data": None,
                "role": None
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




# Usage example:
"""
from fastapi import FastAPI
from exception_handler import register_error_handlers

app = FastAPI()

# Register all exception handlers
register_error_handlers(app)

# Now you can raise custom exceptions in your routes:
@app.get("/test-error")
async def test_error():
    raise NotFoundError("This is a test error")
"""