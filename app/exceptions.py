"""Custom exceptions for the task management API."""


class TaskError(Exception):
    """Base exception for task-related errors."""
    
    def __init__(self, message: str, task_id: int = None):
        self.message = message
        self.task_id = task_id
        super().__init__(self.message)


class TaskNotFoundError(TaskError):
    """Exception raised when a task is not found."""
    
    def __init__(self, task_id: int):
        super().__init__(f"Task {task_id} not found", task_id)


class InvalidTaskStatusError(TaskError):
    """Exception raised when a task has an invalid status for the operation."""
    
    def __init__(self, task_id: int, current_status: str, required_status: str = None):
        if required_status:
            message = f"Task {task_id} has status '{current_status}', expected '{required_status}'"
        else:
            message = f"Task {task_id} has invalid status '{current_status}' for this operation"
        super().__init__(message, task_id)


class TaskValidationError(TaskError):
    """Exception raised when task data is invalid."""
    
    def __init__(self, message: str, task_id: int = None):
        super().__init__(f"Task validation error: {message}", task_id)