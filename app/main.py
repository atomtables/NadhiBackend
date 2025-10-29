from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import BaseSchema, engine
from app.authentication.router import router as auth_router
from app.images.router import router as image_router
from app.volunteering.router import router as volunteer_router
from app.data.router import router as data_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    # import the schemas (just in case they weren't put in use)
    import app.authentication.schemas
    import app.images.schemas
    # Create
    BaseSchema.metadata.create_all(bind=engine)
    yield
    # destroy connection
    engine.dispose()


app = FastAPI(debug=True, lifespan=lifespan)
app.include_router(auth_router)
app.include_router(image_router)
app.include_router(volunteer_router)
app.include_router(data_router)