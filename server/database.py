from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# SQLALCHEMY_DATABASE_URL = os.getenv(
#     "SQLALCHEMY_DATABASE_URL",
#     "postgresql://admin:admin@db:5432/pizzeria"  # Значение по умолчанию
# )
SQLALCHEMY_DATABASE_URL = 'postgresql://admin:admin@localhost:5432/pizzeria' # поменять localhost на db при контейнеризации
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()