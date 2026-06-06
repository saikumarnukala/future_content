"""
YouTube Data API v3 integration for automated uploading.
"""

import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config.settings import settings

def get_youtube_service():
    """Build and return the YouTube service using OAuth2 refresh token."""
    creds = Credentials(
        token=None,
        refresh_token=settings.youtube_refresh_token.get_secret_value(),
        client_id=settings.youtube_client_id,
        client_secret=settings.youtube_client_secret.get_secret_value(),
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('youtube', 'v3', credentials=creds)

def upload_short(video_path: str, script_data: dict) -> str:
    """
    Upload the video to YouTube as a Short.
    Returns the video ID.
    """
    youtube = get_youtube_service()
    
    title = script_data.get("youtube_title", "AI Generated Short")[:100]
    description = script_data.get("youtube_description", "")
    tags = script_data.get("hashtags", [])
    
    if "#Shorts" not in tags:
        tags.insert(0, "#Shorts")
    else:
        tags.remove("#Shorts")
        tags.insert(0, "#Shorts")
        
    clean_tags = [t.lstrip('#') for t in tags[:15]]
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": clean_tags,
            "categoryId": "28"  # Science & Technology
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = request.execute()
    return response.get("id")
