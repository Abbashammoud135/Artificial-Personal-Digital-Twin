"""
Planner Agent - Integration Guide

This guide shows how to use the Planner Agent end-to-end in your application.
"""

from agents.planner.agent import PlannerAgent
from agents.planner.executor import ExecutionPlan, ExecutionGraph


# ============================================================================
# EXAMPLE 1: Basic Planning
# ============================================================================

def example_basic_planning():
    """Example: Simple planning without execution."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Planning")
    print("="*70)
    
    planner = PlannerAgent()
    
    # User request
    user_request = "Analyze my latest blood report"
    
    # Generate plan
    plan = planner.execute(user_request)
    
    # Display results
    print(f"\nGoal: {plan.goal}")
    print(f"Number of tasks: {len(plan.tasks)}\n")
    
    for task in plan.tasks:
        print(f"Task {task.id}: [{task.agent}] {task.action}")
        print(f"  Description: {task.description}")
        if task.depends_on:
            print(f"  Dependencies: {task.depends_on}")
        print()


# ============================================================================
# EXAMPLE 2: Using the Executor
# ============================================================================

def example_executor():
    """Example: Plan execution with mock tasks using LangGraph."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Executing a Plan (LangGraph-based)")
    print("="*70)
    
    planner = PlannerAgent()
    
    # Generate plan
    plan = planner.execute("Analyze my latest blood report and save insights")
    
    # Define a mock executor function
    def execute_task(task):
        """Mock task executor."""
        print(f"\n  ✓ Executing Task {task.id}: {task.agent}.{task.action}")
        print(f"    Description: {task.description}")
        
        # Simulate task execution
        if task.agent == "health" and task.action == "retrieve_report":
            return {"report_id": "12345", "test_date": "2024-06-01"}
        elif task.agent == "health" and task.action == "analyze_report":
            return {"insights": ["Normal", "Good results"], "alerts": []}
        elif task.agent == "memory" and task.action == "save_insights":
            return {"saved": True, "record_id": "rec_789"}
        
        return {"status": "completed"}
    
    # Create execution plan with task executor
    exec_plan = ExecutionPlan(plan, execute_task)
    
    # Execute plan using LangGraph
    print("\nExecuting plan with LangGraph...")
    results = exec_plan.execute()
    
    # Display results
    print(f"\n\nExecution Results:")
    print(f"  Success: {results['success']}")
    print(f"  Status: {results['status']}")
    print(f"  Completed: {results['progress']['completed']} / {results['progress']['total']}")
    
    for task_id, task_result in results["tasks"].items():
        print(f"\n  Task {task_id}: {task_result['status']}")
        if task_result.get('result'):
            print(f"    Result: {task_result['result']}")



# ============================================================================
# EXAMPLE 3: Parallel Task Execution
# ============================================================================

def example_parallel_tasks():
    """Example: Understanding task execution stages (parallelization)."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Understanding Parallel Execution Stages")
    print("="*70)
    
    planner = PlannerAgent()
    
    # Generate plan
    plan = planner.execute("Check my vitals, compare with previous data, and alert if abnormal")
    
    # Create execution graph
    graph = ExecutionGraph(plan)
    
    # Get execution stages
    stages = graph.get_execution_order()
    
    print(f"\nExecution has {len(stages)} stages:\n")
    
    for stage_num, stage_tasks in enumerate(stages, 1):
        print(f"Stage {stage_num} (can execute in parallel):")
        for task in stage_tasks:
            deps = f" (depends on: {task.depends_on})" if task.depends_on else " (no dependencies)"
            print(f"  - Task {task.id}: {task.agent}.{task.action}{deps}")
        print()


# ============================================================================
# EXAMPLE 4: Getting Ready Tasks
# ============================================================================

def example_ready_tasks():
    """Example: Determining which tasks are ready to execute."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Getting Ready Tasks")
    print("="*70)
    
    planner = PlannerAgent()
    plan = planner.execute("Get my latest blood report and retrieve my medical history")
    
    graph = ExecutionGraph(plan)
    
    print(f"\nInitial plan:")
    for task in plan.tasks:
        print(f"  Task {task.id}: {task.agent}.{task.action} (depends_on: {task.depends_on})")
    
    # Get ready tasks
    ready = graph.get_ready_tasks()
    print(f"\n\nReady tasks (no dependencies): {len(ready)}")
    for task in ready:
        print(f"  - Task {task.id}: {task.agent}.{task.action}")
    
    # Simulate task completion
    print(f"\n\nAfter completing tasks 1 and 2:")
    graph.mark_completed(1)
    graph.mark_completed(2)
    
    ready = graph.get_ready_tasks()
    print(f"Ready tasks: {len(ready)}")
    for task in ready:
        print(f"  - Task {task.id}: {task.agent}.{task.action}")


# ============================================================================
# EXAMPLE 5: Error Handling
# ============================================================================

def example_error_handling():
    """Example: Handling task failures with LangGraph."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Error Handling (LangGraph)")
    print("="*70)
    
    planner = PlannerAgent()
    plan = planner.execute("Analyze my blood report and save insights")
    
    task_counter = 0
    
    def execute_task_with_failure(task):
        """Mock executor that fails on task 2."""
        nonlocal task_counter
        task_counter += 1
        
        print(f"\n  Executing Task {task.id}...")
        
        if task.id == 2:
            raise Exception("Service temporarily unavailable")
        
        return {"status": "completed", "task_id": task.id}
    
    # Create execution plan with task executor
    exec_plan = ExecutionPlan(plan, execute_task_with_failure)
    
    # Execute plan
    print("\nExecuting plan with failure on Task 2...")
    results = exec_plan.execute()
    
    # Display error handling
    print(f"\n\nExecution Summary:")
    print(f"  Success: {results['success']}")
    print(f"  Status: {results['status']}")
    if results['error']:
        print(f"  Error: {results['error']}")
    print(f"  Tasks completed: {results['progress']['completed']}")
    print(f"  Tasks failed: {results['progress']['failed']}")


# ============================================================================
# EXAMPLE 6: Progress Tracking
# ============================================================================

def example_progress_tracking():
    """Example: Tracking execution progress."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Progress Tracking")
    print("="*70)
    
    planner = PlannerAgent()
    plan = planner.execute("Analyze my blood report, save insights, and generate alerts")
    
    graph = ExecutionGraph(plan)
    
    print(f"\nInitial Progress:")
    progress = graph.get_progress()
    print(f"  Total: {progress['total']}")
    print(f"  Completed: {progress['completed']}")
    print(f"  Failed: {progress['failed']}")
    print(f"  Pending: {progress['pending']}")
    print(f"  Progress: {progress['percent_complete']:.1f}%")
    
    # Simulate task completion
    print(f"\nAfter completing task 1:")
    graph.mark_completed(1)
    progress = graph.get_progress()
    print(f"  Completed: {progress['completed']}/{progress['total']}")
    print(f"  Progress: {progress['percent_complete']:.1f}%")


# ============================================================================
# EXAMPLE 7: Complete Integration
# ============================================================================

def example_complete_integration():
    """Example: Complete planning and execution workflow with LangGraph."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Complete Integration Workflow (LangGraph)")
    print("="*70)
    
    # Step 1: Generate plan
    print("\n[Step 1] Generating plan...")
    planner = PlannerAgent()
    user_request = "Analyze my latest blood report and save insights"
    plan = planner.execute(user_request)
    
    print(f"✓ Generated plan with {len(plan.tasks)} tasks")
    print(f"  Goal: {plan.goal}")
    
    # Step 2: Analyze execution stages
    print("\n[Step 2] Analyzing execution stages...")
    
    # Define executor
    task_results = {}
    
    def agent_executor(task):
        """Simulate agent execution."""
        # In a real system, this would route to actual agents
        task_results[task.id] = f"Result from {task.agent}.{task.action}"
        return task_results[task.id]
    
    exec_plan = ExecutionPlan(plan, agent_executor)
    stages = exec_plan.get_execution_stages()
    print(f"✓ Plan requires {len(stages)} execution stages")
    
    # Step 3: Execute plan with LangGraph
    print("\n[Step 3] Executing plan with LangGraph...")
    results = exec_plan.execute()
    
    print(f"✓ Execution completed")
    print(f"  Status: {'SUCCESS' if results['success'] else 'FAILED'}")
    print(f"  Tasks: {results['progress']['completed']}/{results['progress']['total']} completed")
    
    # Step 4: Display results
    print("\n[Step 4] Results:")
    for task_id, result in task_results.items():
        print(f"  Task {task_id}: {result}")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("Planner Agent - Integration Examples")
    print("=" * 70)
    
    # Run examples
    example_basic_planning()
    example_executor()
    example_parallel_tasks()
    example_ready_tasks()
    example_error_handling()
    example_progress_tracking()
    example_complete_integration()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")
