import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(String(50), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="favorites")
    destination = relationship("Destination", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint("user_id", "destination_id", name="uq_user_destination_favorite"),
    )
