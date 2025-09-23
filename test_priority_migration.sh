#!/bin/bash

# Create 20 tasks with low priority, then update last two tasks to priority 1 and 2
echo "Creating 20 tasks with low priority..."

task_ids=()

for i in {1..200}; do
    echo "Creating task $i..."
    response=$(curl -s -X POST http://localhost:8000/api/v1/tasks \
        -H "Content-Type: application/json" \
        -d "{\"a\": $((i * 100)), \"b\": $((i * 100)), \"priority\": 3}")

    task_id=$(echo "$response" | jq -r '.id')
    task_ids+=($task_id)
    echo "Task $task_id created"
done

echo ""
echo "Created tasks: ${task_ids[@]}"

# # Get the last two task IDs
# last_task=${task_ids[19]}
# second_last_task=${task_ids[18]}

# echo ""
# echo "Updating task $second_last_task to priority 2..."
# curl -s -X PUT http://localhost:8000/api/v1/tasks/$second_last_task \
#     -H "Content-Type: application/json" \
#     -d '{"priority": 2}' | jq '.'

# echo ""
# echo "Updating task $last_task to priority 1..."
# curl -s -X PUT http://localhost:8000/api/v1/tasks/$last_task \
#     -H "Content-Type: application/json" \
#     -d '{"priority": 1}' | jq '.'