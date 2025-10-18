from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class BaseSchema(DeclarativeBase):
    pass


# TODO: change out for non-in-memory database
engine = create_engine("sqlite://", echo=True)
sessions = Session(engine)

def seed():
    pass