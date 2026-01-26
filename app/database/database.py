import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()


class Base(DeclarativeBase):
    pass

POSTGRES_USER = os.getenv("POSTGRES_USER", "raoUser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "abhinav-kr-rao")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_news_db")

print("env variables loaded successfully")
SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

print("username is: ", POSTGRES_USER)
print("password is: ",POSTGRES_PASSWORD)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        print("db: ", db)
        yield db
    finally:
        db.close()

print("database connection successful")
print("engine: ", engine)
print("SessionLocal: ", SessionLocal)