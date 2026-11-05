from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DestinationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    country: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    image_url: str
    rating: float = Field(0.0, ge=0.0, le=5.0)
    reviews_count: int = Field(0, ge=0)
    price: str
    description: str
    is_featured: bool = False


class DestinationCreateRequest(DestinationBase):
    id: Optional[str] = None


class DestinationUpdateRequest(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    price: Optional[str] = None
    description: Optional[str] = None
    is_featured: Optional[bool] = None


class DestinationResponse(DestinationBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_saved: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
