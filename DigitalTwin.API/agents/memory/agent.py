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

        prompt = MONGO_PROMPT.replace(
            "<<USER_REQUEST>>",
            user_request
        )
        response = self.llm.invoke(prompt)

        response_text = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )
        print("🧠 LLM Response text:", response_text)

        return self.safe_parse_json(response_text)

    async def query_memory(self, user_request: str):

        query = await self.generate_query(
            user_request
        )
        # print("🧠 Generated MongoDB Query:", query)

        results = await self.repo.search(
            query
        )

        return {
            "query": query,
            "results": results
        }


    def safe_parse_json(self, text: str):

        # remove markdown
        text = re.sub(r"```json|```", "", text).strip()

        # replace Mongo ISODate → string
        text = re.sub(
            r'ISODate\("([^"]+)"\)',
            r'"\1"',
            text
        )

        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON found")

        cleaned = text[start:end]

        return json.loads(cleaned)