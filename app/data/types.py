from pydantic import BaseModel
import datetime

class DataOut(BaseModel):
    id: int
    rainfall: int
    temperature: float
    humidity: float
    flood_risk: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True