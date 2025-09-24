# Task Management System

FastAPI task management system with Celery workers and priority queues.

## Features
- **Create Tasks**: Single addition tasks or batch operations
- **Priority Queues**: 3 priority levels (1=high, 2=medium, 3=low)
- **Task Monitoring**: Check task status and results
- **Priority Updates**: Change task priority while running
- **Retry Failed Tasks**: Automatically retry failed tasks

## Build and Run

```bash
docker-compose up -d
```

API will be available at: http://localhost:8000

Swagger documentation: http://localhost:8000/docs

## API Usage

Create a task:
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 20, "priority": 1}'
```

Check tasks:
```bash
curl http://localhost:8000/api/v1/tasks
```

## Architecture
- **API**: FastAPI on port 8000
- **Database**: PostgreSQL
- **Queue**: Redis + Celery workers (3 queues by priority)
- **Workers**: Separate workers for each priority level

## System Diagrams

### Database Schema
```
┌─────────────────┐
│      TASKS      │
├─────────────────┤
│ id (PK)         │
│ type            │
│ status          │
│ priority        │
│ a, b            │
│ result          │
│ pairs           │
│ results         │
│ created_at      │
│ started_at      │
│ finished_at     │
│ error_message   │
└─────────────────┘
```

### System Architecture
```
    Client
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  FastAPI    │────▶│ PostgreSQL   │
│   (API)     │     │ (Database)   │
└─────────────┘     └──────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│   Redis     │────▶│   Celery     │
│  (Queue)    │     │  Workers     │
└─────────────┘     └──────────────┘
                           │
                    ┌──────┼──────┐
                    ▼      ▼      ▼
               High    Medium    Low
              Priority Priority Priority
               Queue    Queue    Queue
```

### Task Processing Sequence
```
Client ──POST /tasks──▶ API ──save──▶ Database
                        │
                        ▼
                    Enqueue Task
                        │
                        ▼
                   Redis Queue ──▶ Worker ──update──▶ Database
                   (by priority)      │
                                     ▼
                               Execute Task
                               (a + b = result)
```

## API Endpoints
- `POST /api/v1/tasks` - Create single task
- `POST /api/v1/tasks/batch` - Create batch task
- `GET /api/v1/tasks` - List tasks
- `GET /api/v1/tasks/{id}` - Get specific task
- `PUT /api/v1/tasks/{id}` - Update task priority
- `POST /api/v1/tasks/{id}/retry` - Retry failed task
- `GET /api/v1/health` - Health check

## Priority System
- **Priority 1**: High priority queue (immediate)
- **Priority 2**: Medium priority queue (5s delay)
- **Priority 3**: Low priority queue (10s delay)


## Local Development

For local development and testing, you can use a virtual environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Testing

Run unit tests:
```bash
make unit-test
```

Run system integration tests:
```bash
make si-test
```
