Feature: Task Creation
  As a user
  I want to create tasks via the API
  So that I can process calculations

  Scenario: Create a simple task
    Given the API is running
    When I create a task with a=10 and b=20
    Then the task should be created successfully
    And the task should have status "pending"
    And the task should have result null

  Scenario: Create a task with custom priority
    Given the API is running
    When I create a task with a=5, b=15, and priority=1
    Then the task should be created successfully
    And the task should have priority 1
    And the task should have status "pending"