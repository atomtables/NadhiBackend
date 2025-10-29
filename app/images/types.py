import datetime
from pydantic import BaseModel

class ImageClassificationOut(BaseModel):
    flood_level: int
    danger_level: int
    annoted_file_name: str

    class Config:
        from_attributes = True

class ImageUploadOut(BaseModel):
    id: int
    file_name: str
    latitude: float | None
    longitude: float | None
    altitude: float | None
    created_at: datetime.datetime
    classification: ImageClassificationOut | None = None

    class Config:
        from_attributes = True

class FinalImageOut(BaseModel):
    id: int
    file_name: str
    question1_answer: str
    question2_answer: str
    question3_answer: str
    created_at: datetime.datetime
    classification: ImageClassificationOut | None = None

    class Config:
        from_attributes = True
