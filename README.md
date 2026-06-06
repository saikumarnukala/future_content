# AI YouTube Shorts Factory

A fully automated cloud-native AI YouTube Shorts factory that runs entirely from GitHub Actions on a daily schedule.

## Features
- Generates scripts via Groq (Llama 3)
- Synthesizes premium voiceover via Deepgram (Aura-2)
- Generates 6 cinematic images via Together AI / Replicate / Stability
- Edits video using FFmpeg (Ken Burns, crossfades, ducked music, baked-in captions)
- Automated quality control scoring
- Uploads to YouTube via Data API v3

## Setup

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in the required API keys.
   ```bash
   cp .env.example .env
   ```

## YouTube OAuth Configuration
To automate YouTube uploads, you must obtain a refresh token:
1. Go to Google Cloud Console, create a project, enable YouTube Data API v3.
2. Create OAuth 2.0 Client IDs (Desktop App).
3. Use a local script to authenticate and obtain the `YOUTUBE_REFRESH_TOKEN`.

## Running the Pipeline
To run the full pipeline locally:
```bash
python pipeline/main.py
```

## Running the API
To start the FastAPI server:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
