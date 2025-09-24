import time
from datetime import datetime, timedelta, timezone

from app.celery_app.app import celery_app
from app.db.session import SessionLocal
from app.models.task import (
    RecurrenceInterval,
    RecurrenceRule,
    Task,
    TaskStatus,
    TaskType,
)
from app.services.task_service import TaskService


# Basic logging to stdout
def log(message: str):
    """Log message with timestamp to stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


# Task configuration
MAX_RETRIES = 3
RETRY_DELAY = 30
MAX_RETRY_DELAY = 300

# Queue delays for different priorities
DELAYS = {
    "high_priority": 0,
    "medium_priority": 5,
    "low_priority": 10,
}


class TaskError(Exception):
    pass


@celery_app.task(
    bind=True, acks_late=True, max_retries=MAX_RETRIES, queue="high_priority"
)
def execute_task_high_priority(self, task_id: str):
    """Execute task on high priority queue with no delay."""
    return _execute_task_with_delay(self, task_id, DELAYS["high_priority"])


@celery_app.task(
    bind=True, acks_late=True, max_retries=MAX_RETRIES, queue="medium_priority"
)
def execute_task_medium_priority(self, task_id: str):
    """Execute task on medium priority queue with 5s delay."""
    return _execute_task_with_delay(self, task_id, DELAYS["medium_priority"])


@celery_app.task(
    bind=True, acks_late=True, max_retries=MAX_RETRIES, queue="low_priority"
)
def execute_task_low_priority(self, task_id: str):
    """Execute task on low priority queue with 10s delay."""
    return _execute_task_with_delay(self, task_id, DELAYS["low_priority"])


def _execute_task_with_delay(self, task_id: str, queue_delay: int):
    """Execute task with specified queue delay and retry logic."""
    db = SessionLocal()
    task = None
    retry_count = self.request.retries
    queue_name = self.request.delivery_info.get("routing_key", "unknown")

    try:
        log(
            f"Starting task {task_id} on {queue_name} queue (attempt {retry_count + 1})"
        )

        if queue_delay > 0:
            log(f"Task {task_id} applying {queue_delay}s delay")
            time.sleep(queue_delay)

        task = db.get(Task, task_id)
        if not task:
            log(f"Task {task_id} not found")
            raise TaskError(f"Task {task_id} not found")

        if task.status not in (
            TaskStatus.pending,
            TaskStatus.queued,
            TaskStatus.failed,
        ):
            log(f"Task {task_id} has invalid status: {task.status}")
            raise TaskError(f"Task {task_id} has invalid status: {task.status}")

        # Update task to running
        task.status = TaskStatus.running
        task.started_at = datetime.now(timezone.utc)
        task.retry_count = retry_count
        db.commit()

        # Execute the actual work
        if task.type == TaskType.single:
            _execute_single_task(task)
        else:
            _execute_batch_task(task)

        # Mark as successful
        task.status = TaskStatus.success
        task.finished_at = datetime.now(timezone.utc)
        db.commit()

        log(f"Task {task_id} completed successfully on {queue_name} queue")

    except TaskError as e:
        log(f"Task {task_id} failed: {e}")
        if task:
            task.status = TaskStatus.failed
            task.error_message = str(e)
            task.finished_at = datetime.now(timezone.utc)
            task.retry_count = retry_count
            db.commit()
        return

    except Exception as e:
        log(
            f"Task {task_id} failed on {queue_name} \
                queue (attempt {retry_count + 1}): {e}"
        )

        if task:
            task.status = (
                TaskStatus.failed if retry_count >= MAX_RETRIES else TaskStatus.queued
            )
            task.error_message = str(e)
            if retry_count >= MAX_RETRIES:
                task.finished_at = datetime.now(timezone.utc)
            task.retry_count = retry_count
            db.commit()

        # Retry with backoff
        if retry_count < MAX_RETRIES:
            retry_delay = min(RETRY_DELAY * (2**retry_count), MAX_RETRY_DELAY)
            log(f"Task {task_id} will retry in {retry_delay} seconds")
            raise self.retry(countdown=retry_delay, exc=e)
        else:
            log(f"Task {task_id} failed permanently after {MAX_RETRIES + 1} attempts")
            raise
    finally:
        db.close()


def _execute_single_task(task: Task):
    """Execute single addition task and store result."""
    if task.a is None or task.b is None:
        raise ValueError("Task missing operands")

    # Test failure case
    if task.a == 99 and task.b == 99:
        raise ValueError("Demo failure: 99+99 always fails")

    task.result = task.a + task.b


def _execute_batch_task(task: Task):
    """Execute batch addition task for multiple pairs of numbers."""
    pairs = task.pairs or []

    # Test failure case
    for pair in pairs:
        if pair.get("a") == 99 and pair.get("b") == 99:
            raise ValueError("Demo failure: batch contains 99+99")

    results = []
    for pair in pairs:
        result = pair.get("a", 0) + pair.get("b", 0)
        results.append(result)

    task.results = results


@celery_app.task(bind=True, queue="medium_priority")
def schedule_recurring_tasks(self):
    """Check for due recurring tasks and create new task instances."""
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        rules = (
            db.query(RecurrenceRule)
            .filter(RecurrenceRule.active.is_(True), RecurrenceRule.next_run_at <= now)
            .all()
        )

        for rule in rules:
            try:
                service = TaskService(db)
                payload = rule.base_payload
                payload["priority"] = rule.priority

                if "pairs" in payload:
                    task = service.create_batch(
                        pairs=payload["pairs"], priority=payload.get("priority", 2)
                    )
                else:
                    task = service.create_single(
                        a=payload.get("a", 0),
                        b=payload.get("b", 0),
                        priority=payload.get("priority", 2),
                    )

                log(f"Created recurring task {task.id} from rule {rule.id}")

                # Update next run time
                if rule.interval_type == RecurrenceInterval.minutely:
                    rule.next_run_at = now + timedelta(minutes=rule.interval_value)
                elif rule.interval_type == RecurrenceInterval.hourly:
                    rule.next_run_at = now + timedelta(hours=rule.interval_value)
                elif rule.interval_type == RecurrenceInterval.daily:
                    rule.next_run_at = now + timedelta(days=rule.interval_value)

                db.commit()
                enqueue_task(task)

            except Exception as e:
                log(f"Failed to process recurring rule {rule.id}: {e}")
                db.rollback()

    except Exception as e:
        log(f"Error in schedule_recurring_tasks: {e}")
    finally:
        db.close()


def get_task_function_by_priority(priority: int):
    """Get appropriate task executor function based on priority level."""
    if priority == 1:
        return execute_task_high_priority
    elif priority == 2:
        return execute_task_medium_priority
    elif priority == 3:
        return execute_task_low_priority
    else:
        log(f"Invalid priority {priority}, using medium priority")
        return execute_task_medium_priority


def enqueue_task(task: Task):
    """Queue task for execution, handling immediate or scheduled execution."""
    now = datetime.now(timezone.utc)
    task_function = get_task_function_by_priority(task.priority)
    queue_name = {1: "high_priority", 2: "medium_priority", 3: "low_priority"}.get(
        task.priority, "medium_priority"
    )

    if task.scheduled_for and task.scheduled_for > now:
        delta = (task.scheduled_for - now).total_seconds()
        task_function.apply_async(args=[str(task.id)], countdown=delta)
        log(f"Task {task.id} scheduled for future execution on {queue_name} queue")
    else:
        task_function.apply_async(args=[str(task.id)])
        log(f"Task {task.id} enqueued for immediate execution on {queue_name} queue")


def migrate_task_to_priority_queue(task: Task, old_priority: int, new_priority: int):
    """Move task between priority queues when priority changes."""
    if task.status not in (TaskStatus.pending, TaskStatus.queued):
        log(
            f"Cannot migrate task {task.id} - \
                status is {task.status}, not pending/queued"
        )
        return False

    if old_priority == new_priority:
        log(f"Task {task.id} priority unchanged ({old_priority}), no migration needed")
        return True

    old_queue = {1: "high_priority", 2: "medium_priority", 3: "low_priority"}.get(
        old_priority, "medium_priority"
    )
    new_queue = {1: "high_priority", 2: "medium_priority", 3: "low_priority"}.get(
        new_priority, "medium_priority"
    )

    log(f"Migrating task {task.id} from {old_queue} queue to {new_queue} queue")

    try:
        task_id_str = str(task.id)

        # Try to revoke from all queues
        for queue_name in ["high_priority", "medium_priority", "low_priority"]:
            try:
                celery_app.control.revoke(
                    task_id_str, terminate=False, signal="SIGUSR1"
                )
            except Exception:
                pass  # Continue if revoke fails

        enqueue_task(task)
        log(f"Successfully migrated task {task.id} to {new_queue} queue")
        return True

    except Exception as e:
        log(f"Failed to migrate task {task.id} from {old_queue} to {new_queue}: {e}")
        return False


def get_queue_name_by_priority(priority: int) -> str:
    """Get queue name string for given priority level."""
    return {1: "high_priority", 2: "medium_priority", 3: "low_priority"}.get(
        priority, "medium_priority"
    )
