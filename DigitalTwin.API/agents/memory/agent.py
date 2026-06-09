import json
import re
from agents.memory.prompts import MONGO_PROMPT
from core.llm.groq_llama_client import get_llm
from database.mongo.repositories.memory_repo import MemoryRepository


class MemoryAgent:

    def __init__(self):
        self.llm = get_llm()
        self.repo = MemoryRepository()

    async def generate_query(self, user_request: str):
        from datetime import datetime
        current_time_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        prompt = MONGO_PROMPT.replace(
            "<<USER_REQUEST>>",
            user_request
        ).replace(
            "<<CURRENT_TIME>>",
            current_time_str
        )
        response = self.llm.invoke(prompt)

        response_text = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )
        print("🧠 LLM Response text:", response_text)

        return self.safe_parse_json(response_text)

    async def generate_answer_from_results(self, user_request: str, results: list) -> str:
        if not results:
            return "I couldn't find any medical records matching your request."

        from agents.memory.prompts import ANSWER_PROMPT
        prompt = ANSWER_PROMPT.format(
            user_request=user_request,
            results=json.dumps(results, default=str)
        )
        response = self.llm.invoke(prompt)

        response_text = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )
        return response_text.strip()

    async def query_memory(self, user_request: str, user_id: str):
        # 1. Translate NL to MongoDB query object
        query = await self.generate_query(
            user_request
        )
        
        # 2. Inject user_id filter programmatically for strict data isolation
        if "filter" not in query or query["filter"] is None:
            query["filter"] = {}
        query["filter"]["user_id"] = user_id

        # print("🧠 Generated MongoDB Query with isolation:", query)

        # 3. Execute query
        results = await self.repo.search(
            query
        )

        # 4. Generate natural language answer based on retrieved documents
        answer = await self.generate_answer_from_results(user_request, results)

        # 5. Persist snapshot/insights to users_memory
        memory_doc = {
            "query": user_request,
            "mongodb_query": query,
            "extracted_answer": answer,
            "result_count": len(results)
        }
        await self.repo.save_memory(user_id, memory_doc)

        return {
            "query": query,
            "results": results,
            "answer": answer,
            "saved_to_memory": True
        }

    async def execute_query(self, query: dict, user_id: str) -> list:
        """
        Directly execute a structured MongoDB query, enforcing user isolation.
        """
        if "filter" not in query or query["filter"] is None:
            query["filter"] = {}
        query["filter"]["user_id"] = user_id

        return await self.repo.search(query)

    async def execute(self, action: str, task: dict) -> dict:
        """
        Execute task actions for the memory agent.
        Supported actions:
          - "query": Query the memory using a natural language request.
          - "save": Save key insights/data to memory.
          - "execute_query": Directly execute a structured MongoDB NoSQL query.
        """
        user_id = task.get("user_id")
        if not user_id:
            raise ValueError("user_id is required in the task payload")

        if action == "query":
            query_text = task.get("query") or task.get("description")
            if not query_text:
                raise ValueError("query or description is required for action 'query'")
            return await self.query_memory(query_text, user_id)

        elif action == "save":
            content = task.get("content")
            if not content:
                raise ValueError("content is required for action 'save'")
            return await self.repo.save_memory(user_id, content)

        elif action == "execute_query":
            query = task.get("query")
            if not query or not isinstance(query, dict):
                raise ValueError("query dictionary is required for action 'execute_query'")
            return await self.execute_query(query, user_id)

        else:
            raise ValueError(f"Unknown action '{action}' for MemoryAgent")

    def safe_parse_json(self, text: str):
        # Remove markdown wrapping code blocks if present
        text = re.sub(r"```json|```", "", text).strip()

        # Remove single line comments (e.g. // comments)
        lines = []
        for line in text.splitlines():
            # Match comment pattern and remove it
            line_no_comment = re.sub(r"\s*//.*$", "", line)
            lines.append(line_no_comment)
        text = "\n".join(lines)

        # Remove block comments (e.g. /* comments */)
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

        # Replace Mongo ISODate → string
        text = re.sub(
            r'ISODate\("([^"]+)"\)',
            r'"\1"',
            text
        )

        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON found in LLM response")

        cleaned = text[start:end]

        return json.loads(cleaned)