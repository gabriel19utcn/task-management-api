# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Endpoints

### Create Single Task
```bash
POST /api/v1/tasks
{
  "a": 10,
  "b": 20,
  "priority": 1
}
```
Response: Task object with ID and status

### Create Batch Task
```bash
POST /api/v1/tasks/batch
{
  "pairs": [{"a": 1, "b": 2}, {"a": 3, "b": 4}],
  "priority": 2
}
```
Response: Batch task object

### List Tasks
```bash
GET /api/v1/tasks?status=success&limit=10
```
Response: Array of tasks with pagination

### Get Specific Task
```bash
GET /api/v1/tasks/{id}
```
Response: Single task object

### Update Task Priority
```bash
PUT /api/v1/tasks/{id}
{
  "priority": 1
}
```
Response: Updated task object

### Retry Failed Task
```bash
POST /api/v1/tasks/{id}/retry
```
Response: Retry confirmation

### Health Check
```bash
GET /api/v1/health
```
Response: Service health status

## Priority Levels
- **Priority 1**: High priority (immediate execution)
- **Priority 2**: Medium priority (5 second delay)
- **Priority 3**: Low priority (10 second delay)

## Task Status
- `pending` - Created but not queued
- `queued` - In queue waiting for worker
- `running` - Currently executing
- `success` - Completed successfully
- `failed` - Failed execution