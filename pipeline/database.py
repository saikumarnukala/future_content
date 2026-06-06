"""
Database configuration and session management using SQLAlchemy.
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from config.settings import settings

engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_date = Column(Date, nullable=False)
    topic = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    script_json = Column(Text, nullable=True)
    title = Column(String, nullable=True)
    narration_text = Column(Text, nullable=True)
    narration_path = Column(String)
    image_prompts = Column(Text)
    image_paths = Column(Text)
    image_urls = Column(Text)
    music_file = Column(String)
    music_license = Column(String)
    video_path = Column(String)
    quality_score = Column(Float)
    qc_breakdown = Column(Text)
    attempt_count = Column(Integer, default=0)
    upload_status = Column(String, default='pending')
    youtube_url = Column(String)
    youtube_id = Column(String)
    publish_date = Column(DateTime)
    error_log = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class TopicHistory(Base):
    __tablename__ = "topic_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    topic = Column(String, nullable=False)
    topic_hash = Column(String, unique=True, nullable=False, index=True)
    run_date = Column(Date, nullable=False)
    embedding = Column(Text)

def init_db():
    """Create the database and tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
