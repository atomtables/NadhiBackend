from datetime import datetime
from unittest.mock import Base
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseSchema

class ImageSchema(BaseSchema):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    altitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # keep track of who the image belongs to (in case it becomes relevant)
    
    user_id = Column(Integer, ForeignKey('users.id'))
    
    user = relationship(
        "UserSchema",
        back_populates="images",
        passive_deletes=True
    )

    # ai classification isn't instantly ready so get picture in the database and wait for
    # ai to finish getting the classification done on the flip side
    classification = relationship(
        "ImageClassificationSchema",
        back_populates="images",
        uselist=False,
        cascade="all, delete-orphan"
    )

class FinalImageSchema(BaseSchema):
    __tablename__ = "final_images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    question1_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    question2_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    question3_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship(
        "UserSchema",
        back_populates="final_images",
        passive_deletes=True
    )

    classification = relationship(
        "FinalImageClassificationSchema",
        back_populates="final_images",
        uselist=False,
        cascade="all, delete-orphan"
    )

class ImageClassificationSchema(BaseSchema):
    __tablename__ = "image_classifications"

    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.id"),
        primary_key=True
    )

    flood_level: Mapped[int] = mapped_column(Integer, nullable=False)
    danger_level: Mapped[int] = mapped_column(Integer, nullable=False)
    annoted_file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    images = relationship(
        "ImageSchema",
        back_populates="classification",
        uselist=False
    )

class FinalImageClassificationSchema(BaseSchema):
    __tablename__ = "final_image_classifications"

    image_id: Mapped[int] = mapped_column(
        ForeignKey("final_images.id"),
        primary_key=True
    )

    flood_level: Mapped[int] = mapped_column(Integer, nullable=False)
    danger_level: Mapped[int] = mapped_column(Integer, nullable=False)
    annoted_file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    final_images = relationship(
        "FinalImageSchema",
        back_populates="classification",
        uselist=False
    )