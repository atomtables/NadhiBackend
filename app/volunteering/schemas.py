from datetime import datetime
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseSchema

class VolunteerSchema(BaseSchema):
    __tablename__ = "volunteers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    user_type: Mapped[str] = mapped_column(String(100), nullable=False)
    help_description: Mapped[str] = mapped_column(String(500), nullable=False)
    image_taken: Mapped[bool] = mapped_column(nullable=False , default=False)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    area_safe: Mapped[bool] = mapped_column(nullable=True , default=True)
    no_medical_emergency: Mapped[bool] = mapped_column(nullable=True, default=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (
        CheckConstraint("NOT (image_taken = TRUE AND image IS NULL)", name="ImageTakenImageNull"),
    )

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship(
        "UserSchema",
        back_populates="volunteers",
        uselist=False,
    )
