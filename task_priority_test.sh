#!/bin/bash

# Create 200 tasks with low priority, then update last 2 tasks to priority 1 and 2.
# Use Swagger UI to verify that tasks are picked up in the correct order.

API_URL="http://localhost:8000/api/v1/tasks"

echo "Creating 200 tasks with low priority..."

task_ids=()

for i in {1..200}; do
    echo "Creating task $i..."
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"a\": $((i * 100)), \"b\": $((i * 100)), \"priority\": 3}")

    task_id=$(echo "$response" | jq -r '.id')
    task_ids+=("$task_id")
    echo "Task $task_id created"
done

echo ""
echo "Created tasks: ${task_ids[@]}"

# Get last two tasks
last_id1=${task_ids[-2]}
last_id2=${task_ids[-1]}

echo ""
echo "Updating last two tasks priorities..."

# Update first one to priority 1
curl -s -X PUT "$API_URL/$last_id1" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d '{"priority": 1}' | jq .

# Update second one to priority 2
curl -s -X PUT "$API_URL/$last_id2" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d '{"priority": 2}' | jq .

echo ""
echo "Updated task $last_id1 -> priority 1"
echo "Updated task $last_id2 -> priority 2"
