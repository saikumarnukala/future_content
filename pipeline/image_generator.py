"""
Image generation module using Pollinations AI (completely free, no API key).
"""

import requests
import base64
import time
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings
from config.prompts import (
    MASTER_IMAGE_PROMPT_TEMPLATE, 
    NEGATIVE_PROMPT, 
    CHARACTER_CONSISTENCY_PROMPT,
    CAMERA_MOVEMENT_ENRICHMENT
)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def generate_image_cloudflare(prompt: str, output_path: Path):
    """Call Cloudflare Workers AI (Stable Diffusion XL). Ultra reliable, zero DNS issues, huge free tier."""
    from config.settings import settings
    
    account_id = settings.cloudflare_account_id.get_secret_value()
    api_token = settings.cloudflare_api_token.get_secret_value()
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "num_steps": 20
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    
    with open(output_path, "wb") as f:
        f.write(response.content)

def generate_scene_images(script_data: dict, output_dir: Path) -> list[str]:
    """Generate all 6 images based on the script scenes."""
    image_paths = []
    scenes = script_data.get("scenes", [])
    
    for i, scene in enumerate(scenes):
        visual_desc = scene.get("visual_description", "")
        mood = scene.get("mood", "tense")
        camera = scene.get("camera_movement", "static-wide")
        
        # Enrich description
        enrichment = CAMERA_MOVEMENT_ENRICHMENT.get(camera, "")
        if enrichment:
            visual_desc += f", {enrichment}"
            
        if i > 0:
            visual_desc += CHARACTER_CONSISTENCY_PROMPT
            
        full_prompt = MASTER_IMAGE_PROMPT_TEMPLATE.format(
            visual_description=visual_desc,
            mood=mood
        )
        
        final_prompt = f"{full_prompt}\nAvoid: {NEGATIVE_PROMPT}"
        
        output_path = output_dir / f"scene_{i+1:02d}.png"
        generate_image_cloudflare(final_prompt, output_path)
        image_paths.append(str(output_path))
        
        time.sleep(2)  # Avoid rate limits
        
    return image_paths
