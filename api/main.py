"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI
from api.routes import health, pipeline, videos
from pipeline.database import init_db

app = FastAPI(title="AI YouTube Shorts Factory API")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(health.router)
app.include_router(pipeline.router)
app.include_router(videos.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
