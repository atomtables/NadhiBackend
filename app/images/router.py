import io
import os
import random
from turtle import back
import requests
import base64
from datetime import datetime
from PIL import Image
from collections import defaultdict

from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks, HTTPException
from geopy.geocoders import Nominatim
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.images.schemas import ImageSchema, ImageClassificationSchema, FinalImageSchema
from app.images.types import ImageUploadOut, FinalImageOut
from app.database import sessions

AI_BACKEND_URL = "http://localhost:5000/predict"

router = APIRouter()

def process_image_with_ai(image_id: int, file_path: str, file_name: str):
    try:
        with open(file_path, "rb") as f:
            files = {'image': (file_name, f, 'image/jpeg')}
            response = requests.post(AI_BACKEND_URL, files=files)
            response.raise_for_status()
            
            ai_data = response.json()
            
            image_base_id = os.path.splitext(file_name)[0]
            annotated_file_name = f'{image_base_id}_annotated.png'
            annotated_file_path = f'images/{annotated_file_name}'
            
            base64_string = ai_data['annotated_image'].split(',')[1]
            annotated_image_data = base64.b64decode(base64_string)
            
            with open(annotated_file_path, "wb") as f:
                f.write(annotated_image_data)

            detected_classes = [d['class'] for d in ai_data.get('detections', [])]
            flood_level = 1 if 'flooding' in detected_classes else 0

            classification_record = ImageClassificationSchema(
                image_id=image_id,
                flood_level=flood_level,
                danger_level=ai_data['danger_level'],
                annoted_file_name=annotated_file_name
            )
            
            # Use a new session for the background task
            sessions.add(classification_record)
            sessions.commit()

    except requests.RequestException as e:
        print(f"Background task failed for image {image_id}: {e}")

async def process_image(file) -> tuple[str, str]:
    # Validate file extension
    allowed_extensions = {'.jpeg', '.jpg', '.heic', '.heif', '.png', '.webp'}
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types are: {', '.join(allowed_extensions)}"
        )

    if not os.path.exists('images'):
        os.mkdir('images')
    
    image_id = str(random.randbytes(8).hex())
    file_name = f'{image_id}{file_ext}'
    file_path = f'images/{file_name}'
    
    image_content = await file.read()
    with Image.open(io.BytesIO(image_content)) as img:
        # Convert to RGB if the image has an alpha channel
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            rgb_img = img.convert('RGB')
            rgb_img.save(f'images/{file_name}', quality=95)
        else:
            # Save in original format if it's already RGB/grayscale
            img.save(f'images/{file_name}', quality=95)
            
    return file_name, file_path

@router.post("/upload/flood")
async def upload_flood_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    latitude: str = Form(...),
    longitude: str = Form(...),
    altitude: float = Form(...),
) -> ImageUploadOut:

    file_name, file_path = await process_image(file)

    record = ImageSchema(
        file_name=file_name,
        latitude=float(latitude),
        longitude=float(longitude),
        altitude=float(altitude),
        created_at=datetime.now()
    )
    
    sessions.add(record)
    sessions.commit()
    sessions.refresh(record)

    background_tasks.add_task(process_image_with_ai, record.id, file_path, file_name)

    return ImageUploadOut(
        id=record.id,
        file_name=record.file_name,
        latitude=record.latitude,
        longitude=record.longitude,
        altitude=record.altitude,
        created_at=record.created_at
    )


@router.post("/upload/final")
async def upload_final_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    q1: str = Form(...),
    q2: str = Form(...),
    q3: str = Form(...),
) -> FinalImageOut:

    file_name, file_path = await process_image(file)

    record = ImageSchema(
        file_name=file_name,
        question1_answer=str(q1),
        question2_answer=str(q2),
        question3_answer=str(q3),
        created_at=datetime.now()
    )
    
    sessions.add(record)
    sessions.commit()
    sessions.refresh(record)

    background_tasks.add_task(process_image_with_ai, record.id, file_path, file_name)

    return FinalImageOut(
        id=record.id,
        file_name=record.file_name,
        question1_answer=record.question1_answer,
        question2_answer=record.question2_answer,
        question3_answer=record.question3_answer,
        created_at=record.created_at
    )

@router.get("/by-state/{state_code}")
async def get_images_by_county(
    type: str | None,
    state_code: str,
    ) -> dict[str, list[ImageUploadOut]]:
    """
    Get all images grouped by county for a given US state.
    Args:
        state_code: Two-letter US state code (e.g., 'NJ', 'NY', 'CA')
    Returns:
        Dictionary mapping county names to lists of images
    """
    state_code = state_code.upper()
    
    # Get all images from database
    stmt = select(ImageSchema).options(joinedload(ImageSchema.classification))
    results = sessions.execute(stmt)
    images = results.scalars().unique().all()
    
    if not images:
        return {}
    
    # Initialize geocoder
    geolocator = Nominatim(user_agent="congressional_image_app")
    
    # Group images by county
    county_images: dict[str, list[ImageUploadOut]] = defaultdict(list)
    
    for image in images:
        # Skip images without coordinates (schema allows nullable)
        if image.latitude is None or image.longitude is None:
            continue
            
        try:
            # Reverse geocode to get location information
            location = geolocator.reverse(  # type: ignore
                f"{image.latitude}, {image.longitude}",
                exactly_one=True            
            )
            
            if not location:
                continue
                
            # Access geocoding results - using type: ignore for geopy
            raw_data = getattr(location, 'raw', None)  # type: ignore
            if not raw_data or not isinstance(raw_data, dict):
                continue
                
            address = raw_data.get('address', {})  # type: ignore
            if not isinstance(address, dict):
                continue
                    
            state = address.get('state')  # type: ignore
            county = address.get('county')  # type: ignore
            
            # Check if this image is in the requested state
            if state and county and isinstance(state, str) and isinstance(county, str):
                # Get ISO code for state matching
                iso_code = address.get('ISO3166-2-lvl4', '')
                if not isinstance(iso_code, str):
                    iso_code = ''
                    
                state_matches = (
                    state_code in state.upper() or 
                    state.upper() in state_code or
                    iso_code.endswith(state_code)
                )
                
                if state_matches:
                    # Clean county name (remove " County" suffix if present)
                    county_name = county.replace(' County', '').strip()
                    
                    image_out = ImageUploadOut.model_validate(image)
                    county_images[county_name].append(image_out)
        except Exception as e:
            # Skip images that fail geocoding
            print(f"Error geocoding image {image.id}: {str(e)}")
            continue
    
    return dict(county_images)
