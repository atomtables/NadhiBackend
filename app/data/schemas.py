from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database import BaseSchema

class DataSchema(BaseSchema):
    __tablename__ = "data"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    rainfall: Mapped[float] = mapped_column(Float, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False)
    flood_risk: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)