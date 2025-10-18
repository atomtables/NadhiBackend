from pydantic import BaseModel


class LoginTypeIn(BaseModel):
    email: str
    password: str