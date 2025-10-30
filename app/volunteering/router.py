from datetime import datetime
import math
from fastapi import APIRouter, File, UploadFile, Form
from sqlalchemy import select

from app.volunteering.schemas import VolunteerSchema
from app.volunteering.types import VolunteerUploadOut, VolunteerPostOut
from app.database import sessions

router = APIRouter()

# API endpoint for someone who needs help
@router.post("/volunteer/{latitude}/{longitude}")
async def upload_volunteer(
    latitude: float,
    longitude: float,
    type: str = Form(...),
    user_type: str = Form(...),
    help_description: str = Form(...),
    image_taken: bool = Form(...),
    image: UploadFile | None = File(...),
    area_safe: bool | None = Form(...),
    no_medical_emergency: bool | None = Form(...),
    location: str = Form(...)
) -> VolunteerUploadOut:
    record = VolunteerSchema(
        type = type,
        timestamp = datetime.now(),
        user_type = user_type,
        help_description = help_description,
        image_taken = image_taken,
        image = image.filename if image else None,
        area_safe = area_safe if area_safe is not None else True,
        no_medical_emergency = no_medical_emergency if no_medical_emergency is not None else True,
        location = location,
        latitude = latitude,
        longitude = longitude
    )

    sessions.add(record)
    sessions.commit()
    sessions.refresh(record)

    return VolunteerUploadOut(
        id = record.id,
        type = record.type,
        timestamp = record.timestamp,
        user_type = record.user_type,
        help_description = record.help_description,
        image_taken = record.image_taken,
        image = record.image,
        area_safe = record.area_safe,
        no_medical_emergency = record.no_medical_emergency,
        location = record.location,
        latitude = record.latitude,
        longitude = record.longitude
    )
    
# API endpoint to get list of people who need help
@router.get("/volunteer/{latitude}/{longitude}")
async def get_volunteer_posts(
    longitude: float,
    latitude: float
) -> list[VolunteerPostOut]:
    
    stmt = select(VolunteerSchema)
    volunteerPosts = sessions.execute(stmt).scalars().all()

    posts: list[VolunteerPostOut] = []
    for volunteerPost in volunteerPosts:
        lat1 = float(latitude)
        lon1 = float(longitude)
        lat2 = float(volunteerPost.latitude)
        lon2 = float(volunteerPost.longitude)

        # Haversine formula
        r = 3958.8  # Earth radius in miles
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        distance = round(r * c, 2)

        posts.append(VolunteerPostOut(
            id = volunteerPost.id,
            type = volunteerPost.type,
            timestamp = volunteerPost.timestamp,
            user_type = volunteerPost.user_type,
            help_description = volunteerPost.help_description,
            image_taken = volunteerPost.image_taken,
            image = volunteerPost.image,
            area_safe = volunteerPost.area_safe,
            no_medical_emergency = volunteerPost.no_medical_emergency,
            location = volunteerPost.location,
            latitude = volunteerPost.latitude,
            longitude = volunteerPost.longitude,
            distance = distance
        ))

    return posts