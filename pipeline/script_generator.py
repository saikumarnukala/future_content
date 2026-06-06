"""
Script generation module using Groq Llama 3.
"""

import json
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from config.prompts import SCRIPT_GENERATION_SYSTEM_PROMPT, SCRIPT_GENERATION_USER_PROMPT

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_script(topic: str, avoid_topics: list[str]) -> dict:
    """Generate script JSON from Groq."""
    client = Groq(api_key=settings.groq_api_key.get_secret_value())
    
    avoid_str = "\n".join(f"- {t}" for t in avoid_topics) if avoid_topics else "None"
    
    prompt = SCRIPT_GENERATION_USER_PROMPT.format(
        topic=topic,
        avoid_topics=avoid_str
    )
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SCRIPT_GENERATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.85,
        top_p=0.92,
        max_tokens=1200,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    
    # Clean up potential markdown formatting
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    try:
        script_data = json.loads(content)
        validate_script(script_data)
        return script_data
    except Exception as e:
        raise ValueError(f"Failed to parse or validate script JSON: {e}\nContent: {content}")

def validate_script(script_data: dict):
    """Quality gates for script."""
    hook = script_data.get("hook", "").lower()
    if hook.startswith("in a world") or hook.startswith("imagine if"):
        raise ValueError("Hook failed quality gate: Starts with banned phrase.")
    
    scenes = script_data.get("scenes", [])
    if len(scenes) != 6:
        raise ValueError(f"Expected 6 scenes, got {len(scenes)}")
        
    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "")
        word_count = len(narration.split())
        if word_count > 35:
            raise ValueError(f"Scene {i+1} narration exceeds 35 words (count: {word_count})")
            
    total_narration = script_data.get("full_narration", "")
    total_words = len(total_narration.split())
    if total_words < 70:
        raise ValueError(f"Total narration word count {total_words} is too low for a 30-45s video. Regenerate with longer, more descriptive sentences.")
