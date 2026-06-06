"""Video database routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from api.schemas import VideoResponse
from pipeline.database import get_db, Video

router = APIRouter(prefix="/videos", tags=["videos"])

@router.get("/", response_model=List[VideoResponse])
def get_videos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    videos = db.query(Video).order_by(Video.id.desc()).offset(skip).limit(limit).all()
    return videos

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video
