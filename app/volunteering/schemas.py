from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseSchema

class VolunteerSchema(BaseSchema):
    __tablename__ = "volunteers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type_of_help: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship(
        "UserSchema",
        back_populates="volunteers",
        uselist=False,
    )
