from typing import Dict, Any, List, Set


class AgentManager:

    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents

    def get_agent(self, name: str):
        return self.agents.get(name)


class ExecutionEngine:

    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager

        self.results: Dict[int, Any] = {}
        self.completed: Set[int] = set()
        self.failed: Set[int] = set()

    # =====================================================
    # EXECUTE PLAN
    # =====================================================
    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:

        tasks = plan.get("tasks", [])
        remaining = tasks.copy()

        while remaining:

            progress_made = False

            for task in remaining[:]:

                task_id = task["id"]
                agent_name = task["agent"]
                action = task["action"]
                description = task.get("description", "")
                deps = task.get("depends_on", [])

                # ----------------------------
                # dependency failed
                # ----------------------------
                if any(d in self.failed for d in deps):
                    self.failed.add(task_id)
                    self.results[task_id] = {
                        "status": "failed",
                        "description": description,
                        "error": "Dependency failed"
                    }
                    remaining.remove(task)
                    progress_made = True
                    continue

                # ----------------------------
                # wait for dependencies
                # ----------------------------
                if not all(d in self.completed for d in deps):
                    continue

                # ----------------------------
                # get agent
                # ----------------------------
                agent = self.agent_manager.get_agent(agent_name)

                if not agent:
                    self.failed.add(task_id)
                    self.results[task_id] = {
                        "status": "failed",
                        "description": description,
                        "error": f"Agent '{agent_name}' not found"
                    }
                    remaining.remove(task)
                    progress_made = True
                    continue

                # ----------------------------
                # execute task
                # ----------------------------
                try:
                    result = agent.execute(action, task)

                    self.completed.add(task_id)
                    self.results[task_id] = {
                        "status": "success",
                        "description": description,
                        "result": result
                    }

                except Exception as e:
                    self.failed.add(task_id)
                    self.results[task_id] = {
                        "status": "failed",
                        "description": description,
                        "error": str(e)
                    }

                remaining.remove(task)
                progress_made = True

            if not progress_made:
                raise RuntimeError("Deadlock detected in task dependencies")

        return self._build_response(plan)

    # =====================================================
    # FINAL OUTPUT
    # =====================================================
    def _build_response(self, plan: Dict[str, Any]) -> Dict[str, Any]:

        return {
            "goal": plan.get("goal"),
            "success": len(self.failed) == 0,
            "completed_tasks": len(self.completed),
            "failed_tasks": len(self.failed),
            "tasks": self.results
        }