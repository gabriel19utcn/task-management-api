from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.celery_app.tasks import enqueue_task
from app.db.session import get_db
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
    service = TaskService(db)
    items, total = service.list_tasks(
        status=status, type_=type, limit=limit, offset=offset
    )
    return {"items": items, "total": total}


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.priority is not None:
        task = service.update_priority(task, task_update.priority)
    else:
        db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    service.delete(task)


@router.post("/{task_id}/retry", response_model=RetryResponse)
def retry_task(task_id: int, db: Session = Depends(get_db)):
    service = TaskService(db)
    task = service.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in [TaskStatus.failed]:
        raise HTTPException(status_code=400, detail="Only failed tasks can be retried")

    task.status = TaskStatus.pending
    task.error_message = None
    task.started_at = None
    task.finished_at = None
    db.commit()
    enqueue_task(task)

    return RetryResponse(task_id=task.id, retried=True)
