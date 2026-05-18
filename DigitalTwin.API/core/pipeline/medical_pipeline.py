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
from tools.pdf_tool import PDFTool
from core.llm.medical_chain import MedicalChain

class MedicalPipeline:
    
    def process_pdf(self, file_path):
        start_timee = datetime.datetime.now()
        lab_results = PDFTool.extract_tables(file_path)
        medical_analysis = MedicalChain()
        analysis_result = medical_analysis.analyze(lab_results)
        end_timee = datetime.datetime.now()
        return {
            "execution_time": str(end_timee - start_timee),
            "lab_results":  lab_results,
            "analysis_result": analysis_result
        }