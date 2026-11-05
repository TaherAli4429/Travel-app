import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(String(50), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="reviews")
    destination = relationship("Destination", back_populates="reviews")
