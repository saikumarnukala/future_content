"""
Topic Generation and Deduping module.
"""

import random
import hashlib
from datetime import date
from sqlalchemy.orm import Session
from difflib import SequenceMatcher
from pipeline.database import TopicHistory, Video

# Allowed genres
GENRES = [
    "POV Future Stories",
    "Future Technology",
    "Future Cities",
    "Future AI Civilizations",
    "Life in 2050",
    "Life in 2100",
    "Life on Mars",
    "Sci-Fi Storytelling"
]

def get_next_genre(db: Session) -> str:
    """Rotate genres, ensuring no consecutive repeats."""
    available = GENRES.copy()
    last_video = db.query(Video).order_by(Video.id.desc()).first()
    if last_video and last_video.genre in available:
        available.remove(last_video.genre)
    
    return random.choice(available)

def get_recent_topics(db: Session, limit: int = 30) -> list[str]:
    """Retrieve the last N topics from the database."""
    recent = db.query(TopicHistory).order_by(TopicHistory.id.desc()).limit(limit).all()
    return [r.topic for r in recent]

def compute_similarity(text1: str, text2: str) -> float:
    """Compute basic string similarity."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def generate_topic(db: Session, client) -> tuple[str, str]:
    """
    Generate a new topic using Groq, ensuring it's unique.
    Returns (topic, genre).
    """
    genre = get_next_genre(db)
    recent_topics = get_recent_topics(db)
    avoid_str = "\n".join(f"- {t}" for t in recent_topics) if recent_topics else "None"
    
    prompt = f"""Generate a highly specific, unique YouTube Short topic for the genre: {genre}.
It must be 1 sentence.
Do not include prefixes or quotes.
Avoid these previous topics:
{avoid_str}"""
    
    max_attempts = 5
    for _ in range(max_attempts):
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a creative director."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.9,
            max_tokens=50
        )
        topic = response.choices[0].message.content.strip().strip('"')
        
        # Check similarity against all recent topics
        is_unique = True
        for prev_topic in recent_topics:
            sim = compute_similarity(topic, prev_topic)
            if sim > 0.82:
                is_unique = False
                break
                
        if is_unique:
            # Store it
            topic_hash = hashlib.sha256(topic.encode()).hexdigest()
            new_hist = TopicHistory(
                topic=topic,
                topic_hash=topic_hash,
                run_date=date.today(),
                embedding=""
            )
            db.add(new_hist)
            db.commit()
            return topic, genre
            
    raise Exception("Failed to generate a unique topic after multiple attempts.")
