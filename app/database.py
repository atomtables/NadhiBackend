from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} 
)

BaseSchema = declarative_base()

sessions = Session(engine)

def seed():
    pass