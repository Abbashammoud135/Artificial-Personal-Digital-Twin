import json
import re

from agents.memory.prompts import MONGO_PROMPT
from core.llm.groq_llama_client import get_llm


class MemoryAgent:
    """
    Converts Natural Language → MongoDB Query (Digital Twin Memory Layer)
    """

    def __init__(self):
        # initialize LLM once
        self.llm = get_llm()

    def nl_to_mongo(self, user_request: str) -> str:
        """
        Main pipeline: NL → MongoDB query
        """

        # 1. Format prompt
        prompt = MONGO_PROMPT.format(input=user_request)

        # 2. Call LLM (LangChain-style or wrapper)
        response = self.llm.invoke(prompt)

        # 3. Extract raw text
        response_text = (
            response.content if hasattr(response, "content")
            else str(response)
        )

        # 4. Extract MongoDB query safely
        mongo_query = self._extract_mongo_query(response_text)

        # 5. Validate query
        # self._validate_query(mongo_query)

        return mongo_query

    # -----------------------------
    # EXTRACTION
    # -----------------------------
    def _extract_mongo_query(self, text: str) -> str:
        """
        Extract db.medical_documents query from LLM output
        """

        if not text:
            return ""

        # remove markdown formatting
        text = text.replace("```js", "").replace("```", "").strip()

        # Try to extract only MongoDB query block
        match = re.search(r"(db\.medical_documents\..+)", text)

        if match:
            return match.group(1).strip()

        # fallback: return cleaned text
        return text

    # -----------------------------
    # VALIDATION
    # -----------------------------
    def _validate_query(self, query: str):
        """
        Safety + schema validation
        """

        if not query:
            raise ValueError("Empty MongoDB query generated")

        # must target correct collection
        if "db.medical_documents" not in query:
            raise ValueError("Invalid collection in query")

        # block dangerous operations
        dangerous_ops = ["drop", "delete", "update", "remove", "insert"]
        if any(op in query.lower() for op in dangerous_ops):
            raise ValueError("Dangerous MongoDB operation blocked")

        return True