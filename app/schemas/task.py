"""
Task schemas for the task management API.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.models.task import RecurrenceInterval, TaskStatus, TaskType

Priority = int  # 1 (highest) .. 3 (lowest) priority levels


class RecurringIn(BaseModel):
    interval_type: RecurrenceInterval
    interval_value: int = Field(
        ge=0, le=1440
    )  # 0 = run once, 1+ = recurring with interval

    @validator("interval_value")
    def validate_interval_value(cls, v, values):
        # interval_value = 0 means "run once" (no recurrence)
        if v == 0:
            return v

        interval_type = values.get("interval_type")
        if (
            interval_type == RecurrenceInterval.minutely and v > 1440
        ):  # Max 24 hours in minutes
            raise ValueError("minutely interval_value cannot exceed 1440 (24 hours)")
        elif (
            interval_type == RecurrenceInterval.hourly and v > 720
        ):  # Max 30 days in hours
            raise ValueError("hourly interval_value cannot exceed 720 (30 days)")
        elif interval_type == RecurrenceInterval.daily and v > 30:  # Max 30 days
            raise ValueError("daily interval_value cannot exceed 30 days")
        return v


class TaskBase(BaseModel):
    priority: Optional[Priority] = Field(default=2, ge=1, le=3)


class TaskCreateSingle(TaskBase):
    a: int
    b: int
    scheduled_for: Optional[datetime] = None
    recurring: Optional[RecurringIn] = None


class Pair(BaseModel):
    a: int
    b: int


class TaskCreateBatch(TaskBase):
    pairs: List[Pair] = Field(min_items=1, max_items=500)
    scheduled_for: Optional[datetime] = None
    recurring: Optional[RecurringIn] = None


class TaskUpdate(BaseModel):
    priority: Optional[Priority] = Field(default=None, ge=1, le=3)


class RecurrenceInfo(BaseModel):
    recurrence_id: int
    interval_type: RecurrenceInterval
    interval_value: int
    next_run_at: datetime


class TaskRead(BaseModel):
    id: int
    type: TaskType
    status: TaskStatus
    priority: int
    a: Optional[int] = None
    b: Optional[int] = None
    result: Optional[int] = None
    pairs: Optional[List[dict]] = None
    results: Optional[List[int]] = None
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    recurring: Optional[RecurrenceInfo] = None
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None

    class Config:
        orm_mode = True


class TaskList(BaseModel):
    items: List[TaskRead]
    total: int


class RetryResponse(BaseModel):
    task_id: int
    retried: bool


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
