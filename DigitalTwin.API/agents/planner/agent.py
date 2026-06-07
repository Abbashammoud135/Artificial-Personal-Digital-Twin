from agents.planner.implementation import PlannerImplementation
from agents.planner.schema import Plan


class PlannerAgent:
    """Planner Agent - breaks down user requests into executable tasks."""

    def __init__(self):
        self.impl = PlannerImplementation()
        self.name = "planner"

    def execute(self, request: str) -> Plan:
        """
        Execute the planner to create a plan from a user request.
        
        Args:
            request: The user's goal or request
            
        Returns:
            Plan: A structured plan with tasks
        """
        return self.impl.create_plan(request)

    def get_name(self) -> str:
        """Get the agent name."""
        return self.name
