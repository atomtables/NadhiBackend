from typing import Optional

import jwt
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.authentication.helpers import check_password, encode_jwt
from app.authentication.schemas import UserSchema
from app.authentication.types import LoginTypeIn
from app.constants import Constants
from app.database import sessions

router = APIRouter()

@router.post("/login")
async def login(data: LoginTypeIn):
    user: Optional[UserSchema] = sessions.scalar(select(UserSchema).where(UserSchema.email == data.email))
    if user is None:
        raise HTTPException(status_code=400)
    if not check_password(data.password, user.password_hash):
        raise HTTPException(status_code=400)
    # user is validated !!! using JWT validate who a user is simply
    return encode_jwt(user)