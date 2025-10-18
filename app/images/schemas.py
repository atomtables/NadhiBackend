from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.authentication.models import UserModel
from app.database import BaseModel


class ImageModel(BaseModel):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    altitude: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # keep track of who the image belongs to (in case it becomes relevant)
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="images",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    # ai classification isn't instantly ready so get picture in the database and wait for
    # ai to finish getting the classification done on the flip side
    classification: Mapped["ImageClassificationModel"] = relationship(
        "ImageClassificationModel",
        back_populates="image",
        uselist=False,
        cascade="all, delete-orphan"
    )


class ImageClassificationModel(BaseModel):
    __tablename__ = "image_classifications"

    # foreign key (no need for back reference)
    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.id"),
        primary_key=True
    )

    flood_level: Mapped[int] = mapped_column(Integer, nullable=False)
    damage: Mapped[str] = mapped_column(String(100), nullable=False)
