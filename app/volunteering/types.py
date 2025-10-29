import datetime
from pydantic import BaseModel

class VolunteerUploadOut(BaseModel):
    id: int
    type: str
    timestamp: datetime.datetime
    user_type: str
    help_description: str
    image_taken: bool
    image: str | None
    area_safe: bool | None
    no_medical_emergency: bool | None
    location: str
    latitude: float
    longitude: float
    
    class Config:
        from_attributes = True

class VolunteerPostOut(BaseModel):
    id: int
    type: str
    timestamp: datetime.datetime
    user_type: str
    help_description: str
    image_taken: bool
    image: str | None
    area_safe: bool | None
    no_medical_emergency: bool | None
    location: str
    latitude: float
    longitude: float
    distance: float

    class Config:
        from_attributes = True