from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY
from app.db.base import Base
from datetime import datetime

class ConfluencePage(Base):
    __tablename__ = "confluence_pages"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(String, unique=True, nullable=False)
    space_key = Column(String)
    title = Column(String)

    last_synced_version = Column(Integer)
    last_synced_content = Column(Text)
    last_synced_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False) #hashed / encrypted
    confluence_spaces = Column(ARRAY(String), default=[])