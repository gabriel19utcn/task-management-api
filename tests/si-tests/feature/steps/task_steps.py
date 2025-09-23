import requests
from behave import given, when, then


@given('the API is running')
def step_api_running(context):
    """Check if the API is running."""
    try:
        response = requests.get('http://localhost:8000/api/v1/health', timeout=5)
        assert response.status_code == 200
        context.api_running = True
    except requests.exceptions.RequestException:
        context.api_running = False
        raise AssertionError("API is not running at http://localhost:8000")


@when('I create a task with a={a:d} and b={b:d}')
def step_create_task(context, a, b):
    """Create a task with given a and b values."""
    task_data = {
        "a": a,
        "b": b
    }
    response = requests.post(
        'http://localhost:8000/api/v1/tasks',
        json=task_data,
        timeout=10
    )
    context.response = response
    if response.status_code == 201:
        context.task = response.json()


@when('I create a task with a={a:d}, b={b:d}, and priority={priority:d}')
def step_create_task_with_priority(context, a, b, priority):
    """Create a task with given a, b, and priority values."""
    task_data = {
        "a": a,
        "b": b,
        "priority": priority
    }
    response = requests.post(
        'http://localhost:8000/api/v1/tasks',
        json=task_data,
        timeout=10
    )
    context.response = response
    if response.status_code == 201:
        context.task = response.json()


@then('the task should be created successfully')
def step_task_created(context):
    """Verify task was created successfully."""
    assert context.response.status_code == 201
    assert hasattr(context, 'task')
    assert 'id' in context.task
    assert context.task['id'] is not None


@then('the task should have status "{status}"')
def step_task_status(context, status):
    """Verify task has expected status."""
    assert context.task['status'] == status


@then('the task should have result null')
def step_task_result_null(context):
    """Verify task result is null."""
    assert context.task['result'] is None


@then('the task should have priority {priority:d}')
def step_task_priority(context, priority):
    """Verify task has expected priority."""
    assert context.task['priority'] == priority