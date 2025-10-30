from fastapi import APIRouter
from pydantic import BaseModel
from .tasks import process_daily_automation, send_scheduled_posts

router = APIRouter()

class TaskTrigger(BaseModel):
    task_name: str

@router.post("/trigger")
async def trigger_task(trigger: TaskTrigger):
    if trigger.task_name == "daily_automation":
        task = process_daily_automation.delay()
    elif trigger.task_name == "scheduled_posts":
        task = send_scheduled_posts.delay()
    else:
        return {"error": "Unknown task"}

    return {"task_id": task.id, "status": "queued"}
