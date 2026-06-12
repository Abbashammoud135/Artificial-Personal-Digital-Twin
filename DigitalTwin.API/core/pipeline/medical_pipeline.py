# import re
# import time
# from typing import List, Dict
# from core.llm.medical_chain import MedicalChain
# from core.memory.medical_memory import MedicalMemory
# from concurrent.futures import ThreadPoolExecutor

# class MedicalPipeline:

#     def __init__(self):
#         self.chain = MedicalChain()
#         self.memory = MedicalMemory()

#     # =====================================================
#     # 1. CLEAN TEXT (medical-aware cleanup)
#     # =====================================================
#     def clean_text(self, text: str) -> str:
#         text = text.replace("\n", " ")
#         text = re.sub(r'\s+', ' ', text)

#         # keep medical units intact
#         text = re.sub(r'[^a-zA-Z0-9.%:/<> mgdlMGDL-]', '', text)

#         return text.strip()

#     # =====================================================
#     # 2. MEDICAL CHUNKING (SMARTER)
#     # =====================================================
#     def chunk_text(self, text: str) -> List[Dict]:

#         # split by medical patterns, not just dots
#         separators = r'(?<=\d)\s(?=[A-Z])|\.|;|\n'
#         raw_chunks = re.split(separators, text)

#         chunks = []
#         for i, c in enumerate(raw_chunks):

#             c = c.strip()
#             if len(c) < 8:
#                 continue

#             chunks.append({
#                 "chunk_id": i + 1,
#                 "text": c,
#                 "type": self.detect_type(c),
#                 "severity_hint": self.detect_severity_hint(c)
#             })

#         return chunks

#     # =====================================================
#     # 3. TYPE DETECTION (extended medical coverage)
#     # =====================================================
#     def detect_type(self, text: str) -> str:

#         t = text.lower()

#         if any(k in t for k in ["glucose", "hba1c", "insulin"]):
#             return "diabetes_marker"

#         if any(k in t for k in ["hemoglobin", "rbc", "iron", "ferritin"]):
#             return "anemia_marker"

#         if any(k in t for k in ["cholesterol", "ldl", "hdl", "triglyceride"]):
#             return "cardio_marker"

#         if any(k in t for k in ["bp", "blood pressure", "systolic", "diastolic"]):
#             return "blood_pressure"

#         return "general"

#     # =====================================================
#     # 4. SEVERITY HINT (fast pre-risk scoring)
#     # =====================================================
#     def detect_severity_hint(self, text: str) -> float:
#         numbers = re.findall(r'\d+', text)

#         if not numbers:
#             return 0.0

#         value = int(numbers[0])

#         # rough heuristic scoring
#         if value > 200:
#             return 0.9
#         elif value > 140:
#             return 0.7
#         elif value < 12:
#             return 0.8
#         else:
#             return 0.2

#     # =====================================================
#     # 5. LLM ANALYSIS (STRUCTURED MEDICAL INTELLIGENCE)
#     # =====================================================
#     def analyze_with_llm(self, chunks: List[Dict]):

#         full_text = "\n".join([c["text"] for c in chunks])

#         return self.chain.analyze(full_text)

#     # =====================================================
#     # 6. ADVANCED RISK ENGINE (not just rules)
#     # =====================================================
#     def compute_risk_from_pages(self, pages):

#         all_chunks = []

#         for page in pages:
#             # reuse your old logic lightly
#             chunks = re.split(r'[.;\n]', page)
#             for c in chunks:
#                 if len(c.strip()) > 5:
#                     all_chunks.append({
#                         "text": c,
#                         "type": self.detect_type(c),
#                         "severity_hint": self.detect_severity_hint(c)
#                     })

#         return self.compute_risk(all_chunks)
    
#     def compute_risk(self, chunks: List[Dict]):

#         risk = {
#             "diabetes": [],
#             "anemia": [],
#             "cardio": [],
#         }

#         triggered_rules = []

#         for c in chunks:

#             text = c["text"].lower()
#             value = c.get("severity_hint", 0)

#             # ---------------- DIABETES ----------------
#             if c["type"] == "diabetes_marker":
#                 if value >= 0.7:
#                     risk["diabetes"].append(value)
#                     triggered_rules.append(f"high glucose pattern detected: {text}")

#             # ---------------- ANEMIA ----------------
#             if c["type"] == "anemia_marker":
#                 if value >= 0.7:
#                     risk["anemia"].append(value)
#                     triggered_rules.append(f"low hemoglobin pattern: {text}")

#             # ---------------- CARDIO ----------------
#             if c["type"] == "cardio_marker":
#                 if value >= 0.7:
#                     risk["cardio"].append(value)
#                     triggered_rules.append(f"cholesterol risk pattern: {text}")

#         # FINAL SCORING (weighted average)
#         final_risk = {
#             "diabetes": min(1.0, sum(risk["diabetes"]) / (len(risk["diabetes"]) + 1)),
#             "anemia": min(1.0, sum(risk["anemia"]) / (len(risk["anemia"]) + 1)),
#             "cardio": min(1.0, sum(risk["cardio"]) / (len(risk["cardio"]) + 1)),
#         }

#         return {
#             "risk_scores": final_risk,
#             "rules_triggered": triggered_rules,
#             "confidence": {
#                 "diabetes": len(risk["diabetes"]),
#                 "anemia": len(risk["anemia"]),
#                 "cardio": len(risk["cardio"])
#             }
#         }

#     def process_pages_parallel(self, pages: List[str]):

#         def process_single_page(page_text):
#             cleaned = self.clean_text(page_text)
#             return self.chain.analyze(cleaned)

#         with ThreadPoolExecutor(max_workers=4) as executor:
#             results = list(executor.map(process_single_page, pages))

#         return results
#     # =====================================================
#     # 7. FULL PIPELINE (FINAL OUTPUT FORMAT)
#     # =====================================================
#     def process_pdf(self, file_path: str):
#         print(f"Starting process_pdf for {file_path}")

#         start_time = time.time()

#         # =========================================
#         # 1. EXTRACT PAGES (NEW)
#         # =========================================
#         pages = PDFTool.extract_pages(file_path)
        
#         extract_time = time.time()
#         print(f"extract_pages took {extract_time - start_time:.2f} seconds")
#         return pages

#     # def process_pdf(self, file_path: str):
#         print(f"Starting process_pdf for {file_path}")

#         start_time = time.time()

#         # =========================================
#         # 1. EXTRACT PAGES (NEW)
#         # =========================================
#         pages = PDFTool.extract_pages(file_path)
#         extract_time = time.time()
#         print(f"extract_pages took {extract_time - start_time:.2f} seconds")

#         # =========================================
#         # 2. CLEAN PAGES
#         # =========================================
#         cleaned_pages = [self.clean_text(p) for p in pages if p.strip()]
#         clean_time = time.time()
#         print(f"clean_text (pages) took {clean_time - extract_time:.2f} seconds")

#         # =========================================
#         # 3. MEMORY (use combined text only here)
#         # =========================================
#         combined_text = "\n".join(cleaned_pages)

#         past_context = self.memory.retrieve_similar(combined_text)
#         memory_time = time.time()
#         print(f"memory.retrieve_similar took {memory_time - clean_time:.2f} seconds")

#         # =========================================
#         # 4. PARALLEL LLM (CORE FIX)
#         # =========================================
#         def process_page(page):
#             context = page + "\n\nPAST HISTORY:\n" + str(past_context)
#             return self.chain.analyze(context)

#         from concurrent.futures import ThreadPoolExecutor

#         with ThreadPoolExecutor(max_workers=4) as executor:
#             llm_results = list(executor.map(process_page, cleaned_pages))

#         llm_time = time.time()
#         print(f"Parallel LLM took {llm_time - memory_time:.2f} seconds")

#         # =========================================
#         # 5. MERGE LLM RESULTS
#         # =========================================
#         merged_llm = self.merge_llm_results(llm_results)

#         # =========================================
#         # 6. RISK (now based on pages)
#         # =========================================
#         risk_result = self.compute_risk_from_pages(cleaned_pages)
#         risk_time = time.time()
#         print(f"compute_risk took {risk_time - llm_time:.2f} seconds")

#         # =========================================
#         # 7. STORE MEMORY
#         # =========================================
#         self.memory.add_report(combined_text, {
#             "file": file_path,
#             "risk": risk_result
#         })
#         add_report_time = time.time()
#         print(f"memory.add_report took {add_report_time - risk_time:.2f} seconds")

#         # =========================================
#         # 8. SUMMARY
#         # =========================================
#         summary = self.build_summary(merged_llm, risk_result)
#         summary_time = time.time()
#         print(f"build_summary took {summary_time - add_report_time:.2f} seconds")

#         total_time = summary_time - start_time
#         print(f"Total process_pdf took {total_time:.2f} seconds")

#         return {
#             "pages": cleaned_pages,
#             "past_context": past_context,
#             "llm_analysis": merged_llm,
#             "risk": risk_result,
#             "summary": summary
#         }
  
#     def merge_llm_results(self, results):
#         merged = {
#             "findings": [],
#             "alerts": []
#         }

#         for r in results:
#             merged["findings"].append(r)

#         return merged
#     # =====================================================
#     # 8. HUMAN-LIKE MEDICAL SUMMARY
#     # =====================================================
#     def build_summary(self, llm_result, risk_result):

#         return {
#             "overview": "Medical report analyzed successfully",
#             "key_findings": llm_result,
#             "risk_level": max(risk_result["risk_scores"].values()),
#             "recommendation": self.generate_recommendation(risk_result)
#         }

#     def generate_recommendation(self, risk):

#         max_risk = max(risk["risk_scores"].values())

#         if max_risk > 0.8:
#             return "URGENT: Consult a doctor immediately"
#         elif max_risk > 0.5:
#             return "Schedule a medical check-up soon"
#         else:
#             return "No immediate risk detected"

import datetime
import json
import re
from typing import Any
from tools.pdf_tool import PDFTool
from core.llm.medical_chain import MedicalChain
from core.rag.knowledge_base import KnowledgeBase

class MedicalPipeline:
    def __init__(self, rag_service: KnowledgeBase | None = None):
        self.chain = MedicalChain()
        
        self.rag = rag_service or KnowledgeBase()
        self.rag.initialize()

    def normalize_text(self, text: str) -> str:
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def parse_reference_range(self, reference: str) -> tuple[float, float] | None:
        if not reference:
            return None

        reference = reference.replace("\n", " ").strip()

        match = re.search(r"([\d.]+)\s*[-–]\s*([\d.]+)", reference)
        if match:
            return float(match.group(1)), float(match.group(2))

        match = re.search(r">=\s*([\d.]+)", reference)
        if match:
            return float(match.group(1)), float("inf")

        match = re.search(r">\s*([\d.]+)", reference)
        if match:
            return float(match.group(1)), float("inf")

        match = re.search(r"<=\s*([\d.]+)", reference)
        if match:
            return float("-inf"), float(match.group(1))

        match = re.search(r"<\s*([\d.]+)", reference)
        if match:
            return float("-inf"), float(match.group(1))

        return None

    def compute_risk_profile(self, labs: list[dict[str, Any]]) -> dict[str, Any]:
        anomalies = []
        scores = {
            "cardiovascular": 0,
            "metabolic": 0,
            "general": 0
        }

        for item in labs:
            test_name = item.get("test-name", "").lower()
            value = item.get("value")
            status = item.get("status", "NORMAL")
            reference = item.get("reference", "")
            label = item.get("units", "")

            if not isinstance(value, (int, float)):
                continue

            if status != "NORMAL":
                anomalies.append({
                    "test_name": test_name,
                    "value": value,
                    "status": status,
                    "reference": reference,
                    "units": label
                })

            if any(key in test_name for key in ["cholesterol", "ldl", "hdl", "triglyceride", "blood pressure", "bp"]):
                if status != "NORMAL":
                    scores["cardiovascular"] += 1
            elif any(key in test_name for key in ["glucose", "hba1c", "insulin", "hemoglobin"]):
                if status != "NORMAL":
                    scores["metabolic"] += 1
            else:
                if status != "NORMAL":
                    scores["general"] += 1

        total = sum(scores.values())
        severity = {
            "cardiovascular": min(1.0, scores["cardiovascular"] / 3),
            "metabolic": min(1.0, scores["metabolic"] / 3),
            "general": min(1.0, scores["general"] / 5),
            "overall": min(1.0, total / 6)
        }

        return {
            "anomalies": anomalies,
            "risk_scores": severity,
            "abnormal_count": len(anomalies)
        }

    def _build_rag_query(self, payload):

        if isinstance(payload, str):
            return [payload]

        if not isinstance(payload, list):
            return [str(payload)]

        queries = []

        for item in payload:
            if not isinstance(item, dict):
                continue

            name = item.get("test-name", "").replace("-", " ").strip()
            value = item.get("value", "")
            status = (item.get("status") or "").upper()

            base = f"{name} blood test"

            # 🔥 STATUS-AWARE QUERY ENGINE
            if status == "HIGH":
                query = (
                    f"{base} high {value} what causes elevated levels "
                    f"risks complications treatment how to reduce"
                )

            elif status == "LOW":
                query = (
                    f"{base} low {value} deficiency causes symptoms "
                    f"what does low mean treatment"
                )

            else:  # NORMAL or UNKNOWN
                continue  # skip normal tests for RAG hints, or you can add a generic query if desired
                query = (
                    f"{base} what is it what does it measure normal range "
                    f"how is it interpreted"
                )

            queries.append(query)

        return queries

    def _get_rag_hints(self, payload: Any, k: int = 3) -> list[str]:
        queries = self._build_rag_query(payload)

        # ensure list
        if isinstance(queries, str):
            queries = [queries]

        all_hits = []
        seen = set()

        for query in queries:
            hits = self.rag.retrieve(query, k=k)

            for hit in hits:
                key = (hit.get("source"), hit.get("page"), hit.get("chunk"))

                if key in seen:
                    continue

                seen.add(key)

                all_hits.append(
                    f"{hit.get('source')} page {hit.get('page') or '-'} "
                    f"chunk {hit.get('chunk')}: {hit.get('text')}"
                )

        return all_hits

    def _extract_llm_text(self, response: Any) -> str:
        if isinstance(response, dict):
            content = response.get("content")
            if isinstance(content, str):
                return content.strip()
            return json.dumps(response, indent=2)

        if isinstance(response, str):
            text = response.strip()
            match = re.search(r"content=(['\"])(.*?)(\1)\s*additional_kwargs=", text, re.S)
            if match:
                return match.group(2).strip()
            return text

        if hasattr(response, "content") and isinstance(response.content, str):
            return response.content.strip()

        if hasattr(response, "text") and isinstance(response.text, str):
            return response.text.strip()

        return str(response).strip()

    def _clean_raw_output_text(self, text: str) -> str:
        text = text.strip()

        code_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
        if code_match:
            return code_match.group(1).strip()

        return text

    def parse_llm_response(self, response: Any) -> dict[str, Any]:
        text = self._extract_llm_text(response)

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "raw_output" in parsed and isinstance(parsed["raw_output"], str):
                parsed["raw_output"] = self._clean_raw_output_text(parsed["raw_output"])
            return parsed
        except Exception:
            return {
                "raw_output": self._clean_raw_output_text(text)
            }

    def process_pdf(self, file_path: str) -> dict[str, Any]:
        start_time = datetime.datetime.now()
        lab_results = PDFTool.extract_tables(file_path)
        hints = self._get_rag_hints(lab_results)
        llm_result = self.chain.analyze({
            "labs": lab_results,
            "source": "pdf",
            "rag_hints": hints
        })
        analysis = self.parse_llm_response(llm_result)
        analysis["rag_references"] = hints
        risk = self.compute_risk_profile(lab_results)
        duration = datetime.datetime.now() - start_time

        return {
            "processed_at": datetime.datetime.utcnow().isoformat(),
            "execution_time": str(duration),
            "report_type": "pdf",
            "lab_results": lab_results,
            "analysis": analysis,
            "risk_profile": risk
        }

    def process_text(self, text: str) -> dict[str, Any]:
        cleaned = self.normalize_text(text)
        hints = self._get_rag_hints(cleaned)
        llm_result = self.chain.analyze({
            "text": cleaned,
            "source": "note",
            "rag_hints": hints
        })
        analysis = self.parse_llm_response(llm_result)
        analysis["rag_references"] = hints
        risk = {
            "anomalies": [],
            "risk_scores": {},
            "abnormal_count": 0
        }

        return {
            "processed_at": datetime.datetime.utcnow().isoformat(),
            "execution_time": "0:00:00",
            "report_type": "note",
            "text": cleaned,
            "analysis": analysis,
            "risk_profile": risk
        }
        
    def do_i_need_to_use_memory(self, question: str) -> dict[str, Any]:
        prompt ="""You are a medical memory routing assistant.

Determine whether answering the user's question requires searching their stored medical records.

The medical records contain ONLY the following information:

{
  "analysis": {
    "lab_results": [
      {
        "test-name": "...",
        "value": 123,
        "units": "...",
        "status": "NORMAL|HIGH|LOW",
        "reference": "..."
      }
    ],
    "analysis": {
      "summary": "...",
      "cardiovascular_risk": "...",
      "metabolic_risk": "...",
      "key_abnormalities": [...],
      "recommendations": [...],
      "insights": [...]
    },
    "risk_profile": {
      "anomalies": [...],
      "risk_scores": {
        "cardiovascular": 0.0,
        "metabolic": 0.0,
        "general": 0.0,
        "overall": 0.0
      },
      "abnormal_count": 0
    }
  }
}

Rules:

1. Use memory ONLY if the answer depends on the user's stored medical data.
2. The available data is LIMITED to the schema above.
3. Never assume the existence of medications, diagnoses, allergies, doctor notes, imaging reports, surgeries, family history, or vital signs.
4. Generate queries only for information that could exist in the schema.
5. If memory is needed, return a short natural-language retrieval query.
6. If memory is not needed, return:
{
  "need_memory": false,
  "query": null
}
7. if user asking about fields or results non in the schema, memory is not needed, return false and null query
Examples:

Question: What is my last triglycerides value?
Output:
{
  "need_memory": true,
  "query": "latest triglycerides result"
}

Question: What causes high triglycerides?
Output:
{
  "need_memory": false,
  "query": null
}
Question: what do you suggest in this case?
Output:
{
  "need_memory": false,
  "query": null
}since the question is too vague and doesn't specifically ask for stored medical data, we cannot assume memory is needed.

Return ONLY valid JSON.

Question:
{question}"""
        
        llm_result = self.chain.llm.invoke(prompt.replace("{question}", question))
        return self.parse_llm_response(llm_result)
    
    def process_question(self, question: str, user_name: str, memory: str) -> dict[str, Any]:
        cleaned = self.normalize_text(question)
        hints = self._get_rag_hints(cleaned)
        llm_result = self.chain.analyze({
            "question": cleaned,
            "source": "question",
            "rag_hints": hints,
            "user_name": user_name,
            "memory": memory
        })
        analysis = self.parse_llm_response(llm_result)
        # analysis["rag_references"] = hints

        return {
            "processed_at": datetime.datetime.utcnow().isoformat(),
            "execution_time": "0:00:00",
            "report_type": "question",
            "question": cleaned,
            "analysis": analysis,
            "risk_profile": {
                "anomalies": [],
                "risk_scores": {},
                "abnormal_count": 0
            }
        }

    def process_image(self, file_path: str) -> dict[str, Any]:
        return {
            "processed_at": datetime.datetime.utcnow().isoformat(),
            "execution_time": "0:00:00",
            "report_type": "image",
            "error": "Image OCR support is not enabled yet. Add an OCR pipeline to process images.",
            "analysis": None,
            "risk_profile": None
        }
