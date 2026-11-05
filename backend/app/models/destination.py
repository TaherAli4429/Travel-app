import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(150), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    image_url = Column(Text, nullable=False)
    rating = Column(Float, default=0.0, nullable=False)
    reviews_count = Column(Integer, default=0, nullable=False)
    price = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    favorites = relationship("Favorite", back_populates="destination", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="destination", cascade="all, delete-orphan")
