from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.task import (
    RecurrenceInterval,
    RecurrenceRule,
    Task,
    TaskStatus,
    TaskType,
)


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_single(
        self,
        a: int,
        b: int,
        priority: int,
        scheduled_for: Optional[datetime],
        recurring: Optional[dict],
    ) -> Task:
        task = Task(
            type=TaskType.single,
            a=a,
            b=b,
            priority=priority,
            scheduled_for=scheduled_for,
        )
        if recurring:
            recurrence_rule = self._create_recurrence_rule(
                recurring,
                base_payload={"a": a, "b": b, "type": "single"},
                priority=priority,
            )
            task.recurrence_rule = recurrence_rule
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def create_batch(
        self,
        pairs: list[dict],
        priority: int,
        scheduled_for: Optional[datetime],
        recurring: Optional[dict],
    ) -> Task:
        task = Task(
            type=TaskType.batch,
            pairs=pairs,
            priority=priority,
            scheduled_for=scheduled_for,
        )
        if recurring:
            recurrence_rule = self._create_recurrence_rule(
                recurring,
                base_payload={"pairs": pairs, "type": "batch"},
                priority=priority,
            )
            task.recurrence_rule = recurrence_rule
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def list_tasks(
        self,
        *,
        status: list[TaskStatus],
        type_: TaskType,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[Task], int]:
        stmt = select(Task)
        if status:
            stmt = stmt.where(Task.status.in_(status))
        if type_:
            stmt = stmt.where(Task.type == type_)

        count_stmt = select(func.count()).select_from(Task)
        if status:
            count_stmt = count_stmt.where(Task.status.in_(status))
        if type_:
            count_stmt = count_stmt.where(Task.type == type_)

        total = self.db.execute(count_stmt).scalar_one()
        items = (
            self.db.execute(
                stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)
            )
            .scalars()
            .all()
        )
        return items, total

    def get(self, task_id: int) -> Optional[Task]:
        return self.db.get(Task, task_id)

    def update_priority(self, task: Task, new_priority: int) -> Task:
        old_priority = task.priority
        task.priority = new_priority
        self.db.commit()
        self.db.refresh(task)

        from app.celery_app.tasks import migrate_task_to_priority_queue

        if old_priority != new_priority:
            migrate_task_to_priority_queue(task, old_priority, new_priority)

        return task

    def delete(self, task: Task):
        self.db.delete(task)
        self.db.commit()

    def retry(self, task: Task) -> Task:
        task.status = TaskStatus.pending
        task.started_at = None
        task.finished_at = None
        task.error_message = None
        if task.type == TaskType.single:
            task.result = None
        else:
            task.results = None
        self.db.commit()
        self.db.refresh(task)
        return task

    def _create_recurrence_rule(
        self, recurring: dict, base_payload: dict, priority: int
    ) -> RecurrenceRule:
        interval_type = RecurrenceInterval(recurring["interval_type"])
        interval_value = recurring["interval_value"]
        next_run_at = datetime.now(timezone.utc)
        rule = RecurrenceRule(
            interval_type=interval_type,
            interval_value=interval_value,
            next_run_at=next_run_at,
            base_payload=base_payload,
            priority=priority,
        )
        self.db.add(rule)
        self.db.flush()
        return rule

    def due_recurrences(self, now: datetime) -> list[RecurrenceRule]:
        stmt = select(RecurrenceRule).where(
            RecurrenceRule.active.is_(True), RecurrenceRule.next_run_at <= now
        )
        return self.db.execute(stmt).scalars().all()

    def advance_recurrence(self, rule: RecurrenceRule):
        if rule.interval_value == 0:
            rule.active = False
            self.db.commit()
            return

        if rule.interval_type == RecurrenceInterval.minutely:
            delta = timedelta(minutes=rule.interval_value)
        elif rule.interval_type == RecurrenceInterval.hourly:
            delta = timedelta(hours=rule.interval_value)
        else:
            delta = timedelta(days=rule.interval_value)
        rule.next_run_at = rule.next_run_at + delta
        self.db.commit()
