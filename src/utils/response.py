from typing import Optional, Any
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from src.v1.base.schema import ErrorResponse, SuccessResponse

def success_response(status_code: int, message: str="success", data: Optional[Any] = None):
    '''Returns a JSON response for success responses'''
    response_content = SuccessResponse(message=message, data=data)
    return JSONResponse(status_code=status_code, content=jsonable_encoder(response_content.model_dump()))

def error_response(status_code: int, message: str, error_code: Optional[str] = None, resolution: Optional[str] = None, data: Optional[Any] = None):
    '''Returns a JSON response for error responses'''
    response_content = ErrorResponse(message=message, error_code=error_code, resolution=resolution, data=data)
    return HTTPException(status_code=status_code, detail=jsonable_encoder(response_content.model_dump()))