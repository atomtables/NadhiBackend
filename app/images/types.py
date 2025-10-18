import datetime
from pydantic import BaseModel

class ImageUploadOut(BaseModel):
    id: int
    file_name: str
    latitude: float | None
    longitude: float | None
    altitude: float | None
    created_at: datetime.datetime