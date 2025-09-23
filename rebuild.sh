#!/bin/bash

echo "Task Management System - Complete Rebuild"
echo "========================================"

# Function to check if container is healthy
check_health() {
    local container=$1
    local max_attempts=30
    local attempt=1

    echo "Checking $container health..."
    while [ $attempt -le $max_attempts ]; do
        if docker ps --filter "name=$container" --filter "status=running" --format "{{.Names}}" | grep -q "$container"; then
            echo "✓ $container is running"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts - waiting for $container..."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo "✗ $container failed to start properly"
    return 1
}

# Function to test API health
test_api_health() {
    echo "Testing API health endpoint..."
    local max_attempts=15
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            echo "✓ API health check passed"
            return 0
        fi
        echo "  Attempt $attempt/$max_attempts - waiting for API..."
        sleep 3
        attempt=$((attempt + 1))
    done
    echo "✗ API health check failed"
    return 1
}

# 1. Complete cleanup
echo "1. Complete Docker cleanup..."
docker-compose down --volumes --remove-orphans
docker system prune -af --volumes
docker image prune -af

# 2. Remove any task-management images specifically
echo "2. Removing project images..."
docker images | grep -E "(task-management|task_)" | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true

# 3. Build everything fresh
echo "3. Building all services..."
docker-compose build --no-cache --pull

# 4. Start services
echo "4. Starting all services..."
docker-compose up -d

# 5. Check individual container health
echo "5. Verifying container health..."
sleep 5

check_health "task_db" || exit 1
check_health "task_redis" || exit 1
check_health "task_api" || exit 1
check_health "task_worker_high" || exit 1
check_health "task_worker_medium" || exit 1
check_health "task_worker_low" || exit 1
check_health "task_beat" || exit 1

# 6. Test API functionality
echo "6. Testing API functionality..."
test_api_health || exit 1

# 7. Show final status
echo "7. Final system status:"
docker-compose ps

echo ""
echo "Rebuild completed successfully!"
echo "================================="
echo "Services:"
echo "   • API: http://localhost:8000"
echo "   • Docs: http://localhost:8000/docs"
echo "   • Database: localhost:5432"
echo "   • Redis: localhost:6379"
echo ""
echo "Quick test commands:"
echo "   # Create a task"
echo "   curl -X POST http://localhost:8000/api/v1/tasks \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"a\": 10, \"b\": 20, \"priority\": 1}'"
echo ""
echo "   # Check tasks"
echo "   curl http://localhost:8000/api/v1/tasks"
echo ""
echo "   # Health check"
echo "   curl http://localhost:8000/api/v1/health"