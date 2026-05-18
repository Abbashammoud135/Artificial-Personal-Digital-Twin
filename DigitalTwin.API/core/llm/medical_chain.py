from langchain_core.prompts import ChatPromptTemplate
from core.llm.groq_llama_client import get_llm
import json


class MedicalChain:

    def __init__(self):
        self.llm = get_llm()

        # ----------------------------
        # MEDICAL ANALYSIS PROMPT
        # ----------------------------
        self.prompt = ChatPromptTemplate.from_template("""
You are a medical analysis assistant.

You are NOT a doctor and must not give diagnosis.

Analyze the following structured lab data:

{input}

Return output in this format:

SUMMARY:
- ...

CARDIOVASCULAR RISK:
- ...

METABOLIC RISK:
- ...

KEY ABNORMALITIES:
- ...

RECOMMENDATIONS:
- only general lifestyle suggestions
- no diagnosis
""")

        self.chain = self.prompt | self.llm

    # ----------------------------
    # RUN ANALYSIS
    # ----------------------------
    def analyze(self, labs: dict):
        return self.chain.invoke({
            "input": json.dumps(labs, indent=2)
        })

# from core.llm.gemini_client import get_gemini_client


# class MedicalChain:

#     def __init__(self):
#         self.client = get_gemini_client()

#     def analyze(self, text: str):

#         prompt = f"""
# You are a clinical AI assistant inside a Digital Health System.

# Your job:
# 1. Extract medical entities (glucose, cholesterol, hemoglobin, BP, etc.)
# 2. Detect abnormal values
# 3. Interpret the lab report in simple language
# 4. Identify possible health risks

# Rules:
# - Be precise
# - Do NOT give diagnosis, only risk interpretation
# - Focus on abnormal patterns

# Medical Data:
# {input}

# Return JSON format:
# {{
#   "patient_name": "",
#   "Age": "",
#   "sex": "",
#   "entities": [],
#   "abnormal_values": [],
#   "interpretation": "",
#   "risk_flags": []
# }}
# """

#         response = self.client.models.generate_content(   
#         model="gemini-3.1-flash-lite-preview",
#         contents=prompt
#         )

#         return response.text