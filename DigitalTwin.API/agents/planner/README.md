# Planner Agent

## Overview

The **Planner Agent** is the orchestration brain of the Digital Twin system. It takes user requests and breaks them down into executable tasks with proper dependencies.

## Architecture

```
User Request
    ↓
PlannerAgent.execute(request)
    ↓
PlannerImplementation.create_plan(request)
    ↓
LLM (Groq LLaMA 3.1) → JSON Response
    ↓
JSON Extraction & Validation
    ↓
Plan (Goal + Tasks with Dependencies)
```

## Components

### 1. **Schema** (`agents/planner/schema.py`)
Defines the data structures:
- **Task**: Individual executable unit with id, agent, action, description, and dependencies
- **Plan**: Complete plan with goal and list of tasks

### 2. **Prompt** (`agents/planner/prompts.py`)
LLM instruction template that:
- Explains the planner's role
- Lists available agents (health, memory, action)
- Provides JSON output format with examples
- Emphasizes task dependencies

### 3. **Implementation** (`agents/planner/implementation.py`)
Core logic:
- Calls Groq LLaMA 3.1 LLM via ChatGroq
- Extracts JSON from LLM response (handles markdown blocks)
- Validates against Pydantic schema
- Returns structured Plan object

### 4. **Agent** (`agents/planner/agent.py`)
Main interface:
- Wraps implementation
- Single method: `execute(request: str) -> Plan`
- Can be called standalone or as part of orchestration

### 5. **API Endpoint** (`api/v1/endpoints/planner.py`)
FastAPI route:
```python
POST /api/v1/planner/plan
Body: { "request": "user's goal" }
Response: { "goal": "...", "tasks": [...] }
```

## Usage

### Standalone
```python
from agents.planner.agent import PlannerAgent

planner = PlannerAgent()
plan = planner.execute("Analyze my latest blood report")

print(f"Goal: {plan.goal}")
for task in plan.tasks:
    print(f"  Task {task.id}: {task.agent}.{task.action}")
    if task.depends_on:
        print(f"    → Depends on: {task.depends_on}")
```

### Via HTTP (Swagger UI)
1. Start the server: `python main.py`
2. Visit: `http://localhost:8000/docs`
3. POST to `/api/v1/planner/plan` with request body

## Example Output

**Input:**
```json
{
  "request": "Analyze my latest blood report and save insights"
}
```

**Output:**
```json
{
  "goal": "Analyze my latest blood report and save insights",
  "tasks": [
    {
      "id": 1,
      "agent": "health",
      "action": "retrieve_report",
      "description": "Get latest blood report",
      "depends_on": []
    },
    {
      "id": 2,
      "agent": "health",
      "action": "analyze_report",
      "description": "Analyze the blood report for insights",
      "depends_on": [1]
    },
    {
      "id": 3,
      "agent": "memory",
      "action": "save_insights",
      "description": "Store the analysis results for future reference",
      "depends_on": [2]
    }
  ]
}
```

## Task Dependencies

The planner generates a **task graph** instead of a simple list:
- **Task 1** has no dependencies (can run immediately)
- **Task 2** depends on Task 1 (must wait for Task 1 to complete)
- **Task 3** depends on Task 2 (must wait for Task 1 and Task 2)

This allows for:
- Parallel execution of independent tasks
- Proper sequencing of dependent tasks
- Error handling at task level

## Testing

Run tests with pytest:
```bash
pytest tests/test_planner.py -v
```

Or test specific cases:
```bash
pytest tests/test_planner.py::test_planner_basic -v -s
pytest tests/test_planner.py::test_planner_with_dependencies -v -s
```

## Configuration

LLM Configuration (in `core/llm/groq_llama_client.py`):
- **Model**: `llama-3.1-8b-instant`
- **Temperature**: 0.3 (low randomness for consistent planning)
- **API Key**: `GROQ_API_KEY` environment variable

## Future Enhancements

1. **Multi-step Planning**: Handle complex nested goals
2. **Plan Optimization**: Reorder tasks for efficiency
3. **Error Recovery**: Generate alternative plans on failures
4. **Learning**: Improve prompts based on execution results
5. **Validation**: Pre-flight checks on task feasibility
6. **Plan Caching**: Reuse similar plans for common requests

## Integration

The Planner integrates with:
- **Agents**: health, memory, action (to be implemented)
- **LLM**: Groq LLaMA via LangChain
- **API**: FastAPI for HTTP endpoints
- **Orchestrator**: (Next step) To execute generated plans
