"""Pipeline trigger routes."""

from fastapi import APIRouter, BackgroundTasks, Depends
from api.schemas import PipelineStatusResponse
from pipeline.main import run_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

@router.post("/run", response_model=PipelineStatusResponse)
def trigger_pipeline(background_tasks: BackgroundTasks):
    """
    Trigger the daily pipeline generation asynchronously.
    """
    background_tasks.add_task(run_pipeline)
    return {"status": "accepted", "message": "Pipeline run started in the background."}
