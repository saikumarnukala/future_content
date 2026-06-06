"""
Pydantic schemas for the FastAPI application.
"""

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Dict

class VideoResponse(BaseModel):
    id: int
    run_date: date
    topic: str
    genre: str
    title: str
    quality_score: Optional[float]
    upload_status: str
    youtube_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PipelineStatusResponse(BaseModel):
    status: str
    message: str
