from typing import (  # Import Generic, List, TypeVar
    Any,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
)
from pydantic import BaseModel, ConfigDict




class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None
    resolution: Optional[str] = None
    data: Optional[Any] = None
    role: Optional[str] = None

