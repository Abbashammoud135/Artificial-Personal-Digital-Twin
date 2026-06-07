"""
Test the Planner Agent in isolation.
"""
import json
from agents.planner.agent import PlannerAgent
from agents.planner.schema import Plan


def test_planner_basic():
    """Test basic planning functionality."""
    planner = PlannerAgent()
    
    # Test request
    request = "Analyze my latest blood report"
    
    # Execute
    plan = planner.execute(request)
    
    # Verify structure
    assert isinstance(plan, Plan)
    assert plan.goal is not None
    assert len(plan.tasks) > 0
    
    # Verify task structure
    for task in plan.tasks:
        assert task.id is not None
        assert task.agent is not None
        assert task.action is not None
        assert task.description is not None
        assert isinstance(task.depends_on, list)
    
    print("✓ Basic planning test passed")
    print(f"Goal: {plan.goal}")
    print(f"Tasks: {len(plan.tasks)}")
    for task in plan.tasks:
        print(f"  - Task {task.id}: {task.agent}.{task.action} - {task.description}")
        if task.depends_on:
            print(f"    Depends on: {task.depends_on}")


def test_planner_with_dependencies():
    """Test planning with task dependencies."""
    planner = PlannerAgent()
    
    # Test request
    request = "Analyze my latest blood report and save insights"
    
    # Execute
    plan = planner.execute(request)
    
    # Verify structure
    assert isinstance(plan, Plan)
    assert len(plan.tasks) > 0
    
    # At least one task should have dependencies
    has_dependencies = any(len(task.depends_on) > 0 for task in plan.tasks)
    assert has_dependencies, "Expected at least one task with dependencies"
    
    print("\n✓ Dependency planning test passed")
    print(f"Goal: {plan.goal}")
    print(f"Tasks: {len(plan.tasks)}")
    for task in plan.tasks:
        print(f"  - Task {task.id}: {task.agent}.{task.action}")
        if task.depends_on:
            print(f"    Depends on: {task.depends_on}")


def test_planner_parallel_tasks():
    """Test planning with parallel tasks (no dependencies)."""
    planner = PlannerAgent()
    
    # Test request with multiple independent tasks
    request = "Get my latest blood report and retrieve my medical history"
    
    # Execute
    plan = planner.execute(request)
    
    # Verify we have multiple tasks
    assert len(plan.tasks) >= 2, "Expected at least 2 tasks"
    
    # Count tasks with no dependencies (can run in parallel)
    parallel_tasks = [task for task in plan.tasks if len(task.depends_on) == 0]
    assert len(parallel_tasks) >= 2, "Expected at least 2 parallel tasks"
    
    print("\n✓ Parallel tasks planning test passed")
    print(f"Goal: {plan.goal}")
    print(f"Total tasks: {len(plan.tasks)}")
    print(f"Parallel tasks (no dependencies): {len(parallel_tasks)}")
    for task in plan.tasks:
        print(f"  - Task {task.id}: {task.agent}.{task.action}")
        if task.depends_on:
            print(f"    Depends on: {task.depends_on}")


def test_planner_complex_workflow():
    """Test planning with complex multi-agent workflow."""
    planner = PlannerAgent()
    
    # Complex request
    request = "Check my vitals, compare with previous data, and alert if abnormal"
    
    # Execute
    plan = planner.execute(request)
    
    # Verify structure
    assert isinstance(plan, Plan)
    assert len(plan.tasks) >= 3, "Expected at least 3 tasks for complex workflow"
    
    # Verify task IDs are sequential
    task_ids = [task.id for task in plan.tasks]
    assert task_ids == list(range(1, len(task_ids) + 1)), "Task IDs should be sequential"
    
    # Verify dependencies reference valid task IDs
    for task in plan.tasks:
        for dep_id in task.depends_on:
            assert dep_id in task_ids, f"Task {task.id} depends on non-existent task {dep_id}"
            assert dep_id < task.id, f"Task {task.id} depends on later task {dep_id}"
    
    print("\n✓ Complex workflow planning test passed")
    print(f"Goal: {plan.goal}")
    print(f"Total tasks: {len(plan.tasks)}")
    for task in plan.tasks:
        indent = "  "
        print(f"{indent}- Task {task.id}: {task.agent}.{task.action}")
        if task.depends_on:
            print(f"{indent}  Depends on: {task.depends_on}")


def test_planner_single_task():
    """Test planning for simple single-task request."""
    planner = PlannerAgent()
    
    # Simple request
    request = "Get my latest blood report"
    
    # Execute
    plan = planner.execute(request)
    
    # Verify structure
    assert isinstance(plan, Plan)
    assert len(plan.tasks) >= 1
    
    # First task should have no dependencies
    assert plan.tasks[0].depends_on == [], "First task should have no dependencies"
    
    print("\n✓ Single task planning test passed")
    print(f"Goal: {plan.goal}")
    print(f"Tasks: {len(plan.tasks)}")
    for task in plan.tasks:
        print(f"  - Task {task.id}: {task.agent}.{task.action}")


def test_planner_task_validity():
    """Test that all generated tasks have valid properties."""
    planner = PlannerAgent()
    
    request = "Analyze my latest blood report and save insights"
    plan = planner.execute(request)
    
    valid_agents = {"health", "memory", "action"}
    
    for task in plan.tasks:
        # Verify agent is valid
        assert task.agent in valid_agents, f"Unknown agent: {task.agent}"
        
        # Verify action is not empty
        assert task.action and len(task.action) > 0, "Action cannot be empty"
        
        # Verify description is not empty
        assert task.description and len(task.description) > 0, "Description cannot be empty"
        
        # Verify depends_on contains only earlier task IDs
        for dep_id in task.depends_on:
            assert dep_id < task.id, f"Task {task.id} depends on later task {dep_id}"
    
    print("\n✓ Task validity test passed")
    print(f"All {len(plan.tasks)} tasks are valid")


if __name__ == "__main__":
    print("Testing Planner Agent...\n")
    test_planner_basic()
    test_planner_with_dependencies()
    test_planner_parallel_tasks()
    test_planner_complex_workflow()
    test_planner_single_task()
    test_planner_task_validity()
    print("\n✅ All tests passed!")

