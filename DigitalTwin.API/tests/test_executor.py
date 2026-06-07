"""
Tests for Simple Plan Executor
"""
import pytest
from agents.planner.schema import Plan, Task
from agents.planner.executor import ExecutionPlan, ExecutionGraph


@pytest.fixture
def simple_plan():
    """Create a simple linear plan."""
    return Plan(
        goal="Test goal",
        tasks=[
            Task(id=1, agent="health", action="get", description="Get data", depends_on=[]),
            Task(id=2, agent="health", action="analyze", description="Analyze", depends_on=[1]),
            Task(id=3, agent="memory", action="save", description="Save", depends_on=[2])
        ]
    )


@pytest.fixture
def parallel_plan():
    """Create a plan with parallel tasks."""
    return Plan(
        goal="Test goal",
        tasks=[
            Task(id=1, agent="health", action="get", description="Get vitals", depends_on=[]),
            Task(id=2, agent="memory", action="get", description="Get history", depends_on=[]),
            Task(id=3, agent="health", action="compare", description="Compare", depends_on=[1, 2])
        ]
    )


def test_execution_graph_creation(simple_plan):
    """Test creating an execution graph."""
    graph = ExecutionGraph(simple_plan)
    assert len(graph.tasks_by_id) == 3
    assert graph.tasks_by_id[1].action == "get"
    assert graph.tasks_by_id[2].action == "analyze"
    assert graph.tasks_by_id[3].action == "save"


def test_get_ready_tasks_sequential(simple_plan):
    """Test getting ready tasks in sequential plan."""
    graph = ExecutionGraph(simple_plan)
    
    # Initially, only task 1 should be ready
    ready = graph.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].id == 1
    
    # Mark task 1 as complete
    graph.mark_completed(1)
    ready = graph.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].id == 2
    
    # Mark task 2 as complete
    graph.mark_completed(2)
    ready = graph.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].id == 3


def test_get_ready_tasks_parallel(parallel_plan):
    """Test getting ready tasks in parallel plan."""
    graph = ExecutionGraph(parallel_plan)
    
    # Initially, tasks 1 and 2 should be ready (both have no dependencies)
    ready = graph.get_ready_tasks()
    assert len(ready) == 2
    assert {task.id for task in ready} == {1, 2}
    
    # Mark tasks 1 and 2 as complete
    graph.mark_completed(1)
    graph.mark_completed(2)
    ready = graph.get_ready_tasks()
    assert len(ready) == 1
    assert ready[0].id == 3


def test_mark_failed(simple_plan):
    """Test marking a task as failed."""
    graph = ExecutionGraph(simple_plan)
    
    # Mark task 1 as failed
    graph.mark_failed(1, "Error occurred")
    
    # Task 2 should not be ready (depends on failed task)
    ready = graph.get_ready_tasks()
    assert len(ready) == 0
    
    # Task 1 should be in failed set
    assert 1 in graph.failed_tasks


def test_get_progress(simple_plan):
    """Test getting execution progress."""
    graph = ExecutionGraph(simple_plan)
    
    # Initially 0% complete
    progress = graph.get_progress()
    assert progress["total"] == 3
    assert progress["completed"] == 0
    assert progress["failed"] == 0
    assert progress["pending"] == 3
    assert progress["percent_complete"] == 0
    
    # After completing task 1
    graph.mark_completed(1)
    progress = graph.get_progress()
    assert progress["completed"] == 1
    assert progress["percent_complete"] == pytest.approx(33.33, rel=1)


def test_get_execution_order_sequential(simple_plan):
    """Test getting execution order for sequential plan."""
    graph = ExecutionGraph(simple_plan)
    stages = graph.get_execution_order()
    
    # Should have 3 stages (each task in its own stage)
    assert len(stages) == 3
    assert stages[0][0].id == 1
    assert stages[1][0].id == 2
    assert stages[2][0].id == 3


def test_get_execution_order_parallel(parallel_plan):
    """Test getting execution order for parallel plan."""
    graph = ExecutionGraph(parallel_plan)
    stages = graph.get_execution_order()
    
    # Should have 2 stages: 1 with tasks 1&2, 1 with task 3
    assert len(stages) == 2
    assert len(stages[0]) == 2
    assert {task.id for task in stages[0]} == {1, 2}
    assert len(stages[1]) == 1
    assert stages[1][0].id == 3


def test_circular_dependency_detection():
    """Test that circular dependencies are detected."""
    # Create a plan with circular dependency
    plan = Plan(
        goal="Test goal",
        tasks=[
            Task(id=1, agent="health", action="a", description="A", depends_on=[2]),
            Task(id=2, agent="health", action="b", description="B", depends_on=[1])
        ]
    )
    
    # Should raise ValueError
    with pytest.raises(ValueError, match="Circular dependency"):
        ExecutionGraph(plan)


def test_langgraph_execution(simple_plan):
    """Test simple execution."""
    call_order = []
    
    def mock_executor(task):
        call_order.append(task.id)
        return f"result_{task.id}"
    
    # Create and execute plan
    exec_plan = ExecutionPlan(simple_plan, mock_executor)
    results = exec_plan.execute()
    
    # Verify all tasks executed in correct order
    assert call_order == [1, 2, 3]
    assert results["success"] is True
    assert len(results["tasks"]) == 3
    assert results["status"] == "completed"


def test_langgraph_parallel_execution(parallel_plan):
    """Test execution with parallel tasks."""
    def mock_executor(task):
        return f"result_{task.id}"
    
    # Create and analyze plan
    exec_plan = ExecutionPlan(parallel_plan, mock_executor)
    execution_stages = exec_plan.get_execution_stages()
    
    # Should have 2 stages with parallel first stage
    assert len(execution_stages) == 2
    assert len(execution_stages[0]) == 2  # Tasks 1 and 2 can run in parallel
    assert len(execution_stages[1]) == 1  # Task 3 must run after


def test_langgraph_failure_handling(simple_plan):
    """Test execution with task failure."""
    def mock_executor_with_failure(task):
        if task.id == 2:
            raise Exception("Task 2 failed")
        return f"result_{task.id}"
    
    # Create and execute plan
    exec_plan = ExecutionPlan(simple_plan, mock_executor_with_failure)
    results = exec_plan.execute()
    
    # Verify failure is captured
    assert results["success"] is False
    assert results["status"] == "failed"
    assert results["tasks"][1]["status"] == "completed"
    assert results["tasks"][2]["status"] == "failed"
    assert results["tasks"][3]["status"] == "failed"  # Fails because dep 2 failed


def test_get_task_info_langgraph(simple_plan):
    """Test getting task information after execution."""
    def mock_executor(task):
        return {"data": f"result_{task.id}"}
    
    exec_plan = ExecutionPlan(simple_plan, mock_executor)
    results = exec_plan.execute()
    
    # Get info for task 2
    info = exec_plan.get_task_info(2)
    assert info["id"] == 2
    assert info["agent"] == "health"
    assert info["action"] == "analyze"
    assert info["depends_on"] == [1]
    assert info["status"] == "completed"




if __name__ == "__main__":
    pytest.main([__file__, "-v"])
