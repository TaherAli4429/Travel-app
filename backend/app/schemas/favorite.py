from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.destination import DestinationResponse


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    destination_id: str
    created_at: datetime
    destination: Optional[DestinationResponse] = None


class FavoriteCheckResponse(BaseModel):
    destination_id: str
    is_saved: bool
