import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utc_now():
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class TaskStatus(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"
    revoked = "revoked"


class TaskType(str, enum.Enum):
    single = "single"
    batch = "batch"


class RecurrenceInterval(str, enum.Enum):
    minutely = "minutely"
    hourly = "hourly"
    daily = "daily"


class RecurrenceRule(Base):
    """Database model for task recurrence scheduling rules."""
    __tablename__ = "recurrence_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    interval_type: Mapped[RecurrenceInterval] = mapped_column(
        Enum(RecurrenceInterval), nullable=False
    )
    interval_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    next_run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    base_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="recurrence_rule")


class Task(Base):
    """Database model for tasks that perform addition operations."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[TaskType] = mapped_column(
        Enum(TaskType), nullable=False, default=TaskType.single
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), nullable=False, default=TaskStatus.pending
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=2, index=True
    )

    # Single task fields
    a: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    b: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    result: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Batch payload & results
    pairs: Mapped[Optional[dict]] = mapped_column("pairs", JSON, nullable=True)
    results: Mapped[Optional[dict]] = mapped_column("results", JSON, nullable=True)

    scheduled_for: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    recurrence_rule_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("recurrence_rules.id"), nullable=True, index=True
    )
    recurrence_rule: Mapped[Optional[RecurrenceRule]] = relationship(
        "RecurrenceRule", back_populates="tasks"
    )

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    def mark_running(self):
        """Mark task as currently running and set start time."""
        self.status = TaskStatus.running
        self.started_at = utc_now()

    def mark_success(self):
        """Mark task as successfully completed and set finish time."""
        self.status = TaskStatus.success
        self.finished_at = utc_now()

    def mark_failed(self, error: str):
        """Mark task as failed with error message and set finish time."""
        self.status = TaskStatus.failed
        self.error_message = error
        self.finished_at = utc_now()
