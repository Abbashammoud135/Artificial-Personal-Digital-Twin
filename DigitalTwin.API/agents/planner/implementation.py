import json
import re
from typing import Dict, Any
from agents.planner.schema import Plan
from core.llm.groq_llama_client import get_llm


class PlannerImplementation:
    """Implementation of the Planner Agent logic."""

    def __init__(self):
        self.llm = get_llm()

    def create_plan(self, user_request: str) -> Plan:
        """
        Create a plan by breaking down the user request into tasks.
        
        Args:
            user_request: The user's goal or request
            
        Returns:
            Plan: A structured plan with goals and tasks
        """
        from agents.planner.prompts import PLANNER_PROMPT

        # Format the prompt with the user request
        prompt = PLANNER_PROMPT.format(user_request=user_request)

        # Call the LLM
        response = self.llm.invoke(prompt)

        # Extract JSON from response (response is a LangChain AIMessage)
        response_text = response.content if hasattr(response, 'content') else str(response)
        json_content = self._extract_json(response_text)

        # Parse and validate
        plan_dict = json.loads(json_content)
        plan = Plan(**plan_dict)

        return plan

    def _extract_json(self, response: str) -> str:
        """
        Extract JSON from LLM response, handling markdown code blocks.
        
        Args:
            response: The raw LLM response
            
        Returns:
            str: Valid JSON string
        """
        # Remove markdown code blocks if present
        if "```json" in response:
            match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            if match:
                return match.group(1)
        elif "```" in response:
            match = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
            if match:
                return match.group(1)

        # Try to extract JSON object
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return match.group(0)

        # Return as-is if no blocks found
        return response.strip()
