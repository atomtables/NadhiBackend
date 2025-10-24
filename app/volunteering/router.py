from datetime import datetime
from fastapi import APIRouter, File, UploadFile, Form
from sqlalchemy import select

from app.volunteering.schemas import VolunteerSchema
from app.volunteering.types import VolunteerUploadOut
from app.database import sessions

router = APIRouter()

@router.post("/volunteer")
async def upload_volunteer(
    name: str = Form(...),
    type_of_help: str = Form(...),
    location: str = Form(...)
) -> VolunteerUploadOut:
    
    record = VolunteerSchema(
        name = name,
        type_of_help = type_of_help,
        location = location,
        created_at = datetime.now()
    )

    sessions.add(record)
    sessions.commit()
    sessions.refresh(record)

    return VolunteerUploadOut(
        id = record.id,
        name = record.name,
        type_of_help = record.type_of_help,
        location = record.location,
        created_at = record.created_at
    )
    
@router.get("/volunteer")
async def get_volunteer_posts():
    
    stmt = select(VolunteerSchema)
    volunteerPosts = sessions.execute(stmt).scalars().all()

    posts = []
    for volunteerPost in volunteerPosts:
        posts.append(VolunteerUploadOut(
            id = volunteerPost.id,
            name = volunteerPost.name,
            type_of_help = volunteerPost.type_of_help,
            location = volunteerPost.location,
            created_at = volunteerPost.created_at,
        ))

    return posts