# schemas.py
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseSchema


class UserSchema(BaseSchema):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    images = relationship(
        "ImageSchema",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    final_images = relationship(
        "FinalImageSchema",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    volunteers = relationship(
        "VolunteerSchema",
        back_populates="user",
        cascade="all, delete-orphan"
    )