import bcrypt
import jwt

from app.authentication.schemas import UserSchema
from app.constants import Constants


def get_hashed_password(plain_text_password: str) -> str:
    # Hash a password for the first time
    # (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password.encode(), bcrypt.gensalt()).decode()

def check_password(plain_text_password: str, hashed_password: str) -> bool:
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode(), hashed_password.encode())

def encode_jwt(user: UserSchema) -> str:
    return jwt.encode({
        "id": user.id,
        "firstName": user.first_name,
        "lastName": user.last_name
    }, Constants.PRIVATE_KEY_SECRET, algorithm=Constants.PRIVATE_KEY_ALGORITHM)

def decode_jwt(token: str) -> dict[str, str]:
    return dict(jwt.decode(token, Constants.PRIVATE_KEY_SECRET, algorithms=[Constants.PRIVATE_KEY_ALGORITHM]))
