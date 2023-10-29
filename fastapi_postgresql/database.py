from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URI_DATABASE = "postgresql+psycopg2://postgres:mrinal1729@localhost:5432/quizapp"

engine = create_engine(URI_DATABASE)
Sessionlocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()