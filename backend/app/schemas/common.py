from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    meta: Optional[PaginationMeta] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str = "An error occurred"
    errors: List[str] = []
