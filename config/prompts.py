"""
LLM Prompt templates and Image generation prompts for the pipeline.
"""

# System prompt for Groq Llama 3 script generation
SCRIPT_GENERATION_SYSTEM_PROMPT = """You are a cinematic screenwriter for premium YouTube Shorts. 
Write visceral, specific, emotionally resonant stories. 
Never be generic. Start with action, not explanation. 
Write like the audience can SEE it happening.

Your output MUST be valid JSON matching the required schema exactly.
Do not output any text before or after the JSON.
"""

# JSON Schema instructions for script generation
SCRIPT_GENERATION_USER_PROMPT = """Generate a 30-second YouTube Short script on the following topic:
{topic}

Avoid the following previous topics to ensure uniqueness:
{avoid_topics}

REQUIRED OUTPUT STRUCTURE (strict JSON):
{{
  "title": "Hook-first title, max 60 chars, no clickbait",
  "hook": "Opening line that grabs in 0.5 seconds - specific, visual, provocative",
  "scenes": [
    {{
      "scene_number": 1,
      "duration_seconds": 6,
      "narration": "Voiceover text - conversational, visceral, EXACTLY 15-25 words per scene. Use full descriptive sentences, never short fragments.",
      "visual_description": "Cinematographer-level shot description for image gen",
      "camera_movement": "dolly-in | pan-left | tilt-up | handheld | static-wide",
      "mood": "tense | awe | melancholic | triumphant | eerie | wonder"
    }}
  ],
  "full_narration": "All 6 scenes concatenated for TTS",
  "youtube_title": "SEO-optimized title with primary keyword first",
  "youtube_description": "3-paragraph description: hook -> story -> CTA. 200 words.",
  "hashtags": ["#Tag1", "#Tag2", "#Tag3", "#Tag4", "#Tag5", "#Tag6", "#Tag7", "#Tag8", "#Tag9", "#Tag10", "#Tag11", "#Tag12", "#Tag13", "#Tag14", "#Tag15"],
  "seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "target_emotion": "primary emotion this video should trigger",
  "quality_score": 0
}}

RULES:
- Scene array must contain exactly 6 scenes.
- Hook must NOT start with "In a world" or "Imagine if"
- Each scene narration must be FULL sentences (15 to 30 words). DO NOT write 3-word fragments.
- Story must have: setup -> tension -> resolution arc
- No scene may repeat a visual concept from a prior scene
- Total narration word count MUST be exactly 90-120 words to hit the 30-45 second length mark.
"""

# Master prompt for image generation
MASTER_IMAGE_PROMPT_TEMPLATE = (
    "{visual_description}, cinematic photography, "
    "anamorphic lens flare, volumetric light rays, "
    "8K ultra-detailed, photorealistic, "
    "{mood} atmosphere, Blade Runner 2049 color grade, "
    "depth of field, bokeh background, "
    "rule of thirds composition, "
    "hyperrealistic textures, no text, no watermarks, "
    "aspect ratio 9:16, vertical frame"
)

# Consistency enforcement appended for character continuity
CHARACTER_CONSISTENCY_PROMPT = (
    ", same character as previous scene, consistent appearance, "
    "same clothing, same facial features"
)

# Negative prompt for image generation
NEGATIVE_PROMPT = (
    "cartoon, anime, illustration, painting, drawing, "
    "2D, flat, low quality, blurry, pixelated, "
    "watermark, text, logo, signature, "
    "oversaturated, neon-only, generic stock photo, "
    "distorted faces, extra limbs, deformed"
)

# Camera movement to visual description mapping
CAMERA_MOVEMENT_ENRICHMENT = {
    "dolly-in": "extreme close-up, macro detail, intimate",
    "pan-left": "wide establishing shot, environmental context",
    "tilt-up": "low angle, heroic perspective, sky background",
    "handheld": "dynamic, gritty, documentary feel",
    "static-wide": "symmetrical composition, grand scale, stillness"
}
