from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success_response(status_code: int, data: Optional[dict] = None, message: Optional[str] = None):
    '''Returns a JSON response for success responses'''

    response_data = {
        "status_code": status_code,
        "success": True
    }
    
    if message is not None:
        response_data["message"] = message
    
    if data is not None:
        response_data["data"] = data

    return JSONResponse(status_code=status_code, content=jsonable_encoder(response_data))