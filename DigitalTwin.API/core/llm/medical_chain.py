from langchain_core.prompts import ChatPromptTemplate
from core.llm.groq_llama_client import get_llm
import json


class MedicalChain:

    def __init__(self):
        self.llm = get_llm()

        self.lab_prompt = ChatPromptTemplate.from_template("""
You are a medical intelligence assistant for a personal digital twin.

You are NOT a doctor and you must NOT provide a diagnosis.
Your job is to analyze lab data, highlight non-normal findings, and ground your conclusions in available knowledge hints.

Lab results:
{input}

External evidence from the knowledge base (use only when relevant):
{rag_hints}

Return valid JSON only with the following fields:
{{
  "summary": "...",
  "cardiovascular_risk": "...",
  "metabolic_risk": "...",
  "key_abnormalities": ["..."],
  "recommendations": ["..."],
  "insights": ["..."],
  "rag_references": ["..."],
  "raw_output": "..."
}}

If you cannot parse the input, return a JSON object with a single field called "raw_output" containing the text analysis.
""")

        self.note_prompt = ChatPromptTemplate.from_template("""
You are a medical intelligence assistant for a personal digital twin.

You are NOT a doctor and you must NOT provide a diagnosis.
Your job is to summarize the note, highlight important medical clues, and ground your analysis in available knowledge hints.

Text note:
{input}

External evidence from the knowledge base (use only when relevant):
{rag_hints}

Return valid JSON only with the following fields:
{{
  "summary": "...",
  "key_abnormalities": ["..."],
  "recommendations": ["..."],
  "insights": ["..."],
  "rag_references": ["..."],
  "raw_output": "..."
}}

If you cannot parse the input, return a JSON object with a single field called "raw_output" containing the text analysis.
""")

        self.qa_prompt = ChatPromptTemplate.from_template("""
You are a medical intelligence assistant for a personal digital twin.

You are NOT a doctor and you must NOT provide a diagnosis.
Your job is to answer the user's question using evidence from the knowledge base and the user input.

Question:
{input}

Evidence from the knowledge base:
{rag_hints}

Return valid JSON only with the following fields:
{{
  "summary": "...",
  "recommendations": ["..."],
  "insights": ["..."],
  "rag_references": ["..."],
  "raw_output": "..."
}}

If the answer cannot be supported by the evidence provided, return a JSON object with a single field called "raw_output" containing your honest reasoning.
""")

        self.general_prompt = ChatPromptTemplate.from_template("""
You are a medical intelligence assistant for a personal digital twin.

You are NOT a doctor and you must NOT provide a diagnosis.
Your job is to answer using available input and optional knowledge base hints.

Data:
{input}

Knowledge hints:
{rag_hints}

Return valid JSON only with the following fields:
{{
  "summary": "...",
  "recommendations": ["..."],
  "insights": ["..."],
  "rag_references": ["..."],
  "raw_output": "..."
}}

If you cannot parse the input, return a JSON object with a single field called "raw_output".
""")

    def _invoke(self, prompt: ChatPromptTemplate, values: dict):
        chain = prompt | self.llm
        return chain.invoke(values)

    def _format_rag_hints(self, hints):
        if not hints:
            return "No related knowledge hints were found."

        if isinstance(hints, list):
            return "\n\n".join([f"- {hint}" for hint in hints if hint])

        return str(hints)

    def select_prompt(self, data: dict):
        source = data.get("source", "general")
        if source == "pdf":
            return self.lab_prompt
        if source == "note":
            return self.note_prompt
        if source == "question":
            return self.qa_prompt
        return self.general_prompt

    def analyze(self, data: dict):
        prompt = self.select_prompt(data)
        payload = {
            "input": json.dumps(data, indent=2),
            "rag_hints": self._format_rag_hints(data.get("rag_hints"))
        }
        print(f"Invoking MedicalChain with : {payload}")

        result = self._invoke(prompt, payload)

        if isinstance(result, dict) and isinstance(result.get("content"), str):
            return result["content"].strip()

        if hasattr(result, "content") and isinstance(result.content, str):
            return result.content.strip()

        return result
