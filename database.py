from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = 'mysql+pymysql://root:Jasim%40123@127.0.0.1:3306/fastapi'

engine = create_engine(DB_URL)

Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

