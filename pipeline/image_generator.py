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
def generate_image_huggingface(prompt: str, output_path: Path):
    """Call Hugging Face Inference API. 100% free, no credit card. Works perfectly in cloud."""
    from config.settings import settings
    import time
    
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    
    headers = {
        "Authorization": f"Bearer {settings.image_api_key.get_secret_value()}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "cartoon, anime, illustration, painting, drawing, low quality, blurry, pixelated, watermark, text",
            "num_inference_steps": 25,
            "guidance_scale": 7.5
        }
    }
    
    max_wait = 120
    start_time = time.time()
    
    while True:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        # Handle Hugging Face model loading (cold start)
        if response.status_code == 503:
            if time.time() - start_time > max_wait:
                raise RuntimeError("Hugging Face model took too long to load.")
            print("Model is loading. Waiting 15 seconds...")
            time.sleep(15)
            continue
            
        response.raise_for_status()
        break
    
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
        generate_image_huggingface(final_prompt, output_path)
        image_paths.append(str(output_path))
        
        time.sleep(2)  # Avoid rate limits
        
    return image_paths
