from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.celery_app.tasks import enqueue_task
from app.db.session import get_db
from app.exceptions import InvalidTaskStatusError, TaskNotFoundError
from app.models.task import TaskStatus, TaskType
from app.schemas.task import (
    RetryResponse,
    TaskCreateBatch,
    TaskCreateSingle,
    TaskList,
    TaskRead,
    TaskUpdate,
)
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=201)
def create_single(payload: TaskCreateSingle, db: Session = Depends(get_db)):
    """Create a single task with two integers for addition."""
    service = TaskService(db)
    task = service.create_single(
        a=payload.a,
        b=payload.b,
        priority=payload.priority or 2,
        scheduled_for=payload.scheduled_for,
        recurring=payload.recurring.dict() if payload.recurring else None,
    )
    enqueue_task(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/batch", response_model=TaskRead, status_code=201)
def create_batch(payload: TaskCreateBatch, db: Session = Depends(get_db)):
    """Create a batch task with multiple pairs of integers for addition."""
    service = TaskService(db)
    pairs = [p.dict() for p in payload.pairs]
    task = service.create_batch(
        pairs=pairs,
        priority=payload.priority or 2,
        scheduled_for=payload.scheduled_for,
        recurring=payload.recurring.dict() if payload.recurring else None,
    )
    enqueue_task(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=TaskList)
def list_tasks(
    status: list[TaskStatus] = Query([TaskStatus.success]),
    type: TaskType = Query(TaskType.single, alias="type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get paginated list of tasks filtered by status and type."""
    service = TaskService(db)
    items, total = service.list_tasks(
        status=status, type_=type, limit=limit, offset=offset
    )
    return {"items": items, "total": total}


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a specific task by ID."""
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise TaskNotFoundError(task_id)
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Update task properties, mainly priority."""
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise TaskNotFoundError(task_id)

    if task_update.priority is not None:
        task = service.update_priority(task, task_update.priority)
    else:
        db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task permanently."""
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise TaskNotFoundError(task_id)
    service.delete(task)


@router.post("/{task_id}/retry", response_model=RetryResponse)
def retry_task(task_id: int, db: Session = Depends(get_db)):
    """Retry a failed task by resetting its status and re-enqueuing."""
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise TaskNotFoundError(task_id)

    if task.status not in [TaskStatus.failed]:
        raise InvalidTaskStatusError(task_id, task.status.value, "failed")

    task.status = TaskStatus.pending
    task.error_message = None
    task.started_at = None
    task.finished_at = None
    db.commit()
    enqueue_task(task)

    return RetryResponse(task_id=task.id, retried=True)
