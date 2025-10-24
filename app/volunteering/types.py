import datetime
from pydantic import BaseModel

class VolunteerUploadOut(BaseModel):
    id: int
    name: str
    type_of_help: str
    location: str
    created_at: datetime.datetime
    