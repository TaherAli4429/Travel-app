from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreateRequest(BaseModel):
    destination_id: str
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: str = Field(..., min_length=2, max_length=2000)


class ReviewUpdateRequest(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, min_length=2, max_length=2000)


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    user_name: Optional[str] = None
    destination_id: str
    rating: float
    comment: str
    created_at: datetime
    updated_at: Optional[datetime] = None
