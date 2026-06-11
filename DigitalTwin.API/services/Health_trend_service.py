from collections import defaultdict
from datetime import datetime
import re


class TrendService:

    def __init__(self, medical_repo):
        self.medical_repo = medical_repo

    SYNONYMS = {
        "choelesterolldl": "ldl",
        "cholesterolldl": "ldl",
        "ldlcholesterol": "ldl",

        "cholesterolhdl": "hdl",
        "hdlcholesterol": "hdl",

        "cholesteroltotal": "total_cholesterol",
        "cholesteroltserum": "total_cholesterol",
        "Cholesterol -Serum": "total_cholesterol",
    }
    def normalize_test_name(self, name: str):
        name = name.lower()

        # remove punctuation
        name = re.sub(r"[^a-z0-9\s]", "", name)

        # remove extra spaces
        name = re.sub(r"\s+", " ", name).strip()

        # remove common lab suffix noise
        noise_words = {
            "serum"
        }

        tokens = [
            t for t in name.split()
            if t not in noise_words
        ]

        return "".join(tokens)

    def extract_lab_history(self, reports):

        grouped = defaultdict(list)

        for report in reports:

            analyzed_at = report.get("analyzed_at")
            analysis = report.get("analysis") or {}
            if not analyzed_at:
                analyzed_at = analysis.get("analyzed_at") or analysis.get("processed_at")

            if not analyzed_at:
                continue

            if isinstance(analyzed_at, str):
                try:
                    analyzed_at = datetime.fromisoformat(
                        analyzed_at.replace("Z", "")
                    )
                except:
                    continue

            lab_results = report.get("lab_results") or analysis.get("lab_results", [])
            for lab in lab_results:

                test_name = lab.get("test-name")
                value = lab.get("value")

                if test_name is None or value is None:
                    continue

                try:
                    value = float(value)
                except:
                    continue

                key = self.normalize_test_name(test_name)
                key = self.SYNONYMS.get(key, key)
                grouped[key].append({
                    "test_name": test_name,
                    "value": value,
                    "date": analyzed_at,
                    "status": lab.get("status"),
                    "units": lab.get("units")
                })

        for k in grouped:
            grouped[k].sort(
                key=lambda x: x["date"]
            )

        return grouped

    def compute_trend(self, values):

        if len(values) < 2:
            return "INSUFFICIENT_DATA"

        first = values[0]
        last = values[-1]

        change = last - first

        threshold = max(abs(first) * 0.05, 1)

        if abs(change) < threshold:
            return "STABLE"

        return (
            "INCREASING"
            if change > 0
            else "DECREASING"
        )

    def build_trend_response(self, grouped_data):

        result = {}

        for test_key, records in grouped_data.items():

            values = [
                r["value"]
                for r in records
            ]

            if not values:
                continue

            result[test_key] = {
                "test_name": records[-1]["test_name"],
                "units": records[-1]["units"],
                "trend": self.compute_trend(values),
                "latest_value": values[-1],
                "min": min(values),
                "max": max(values),
                "avg": round(sum(values) / len(values), 2),

                "points": [
                    {
                        "date": r["date"],
                        "value": r["value"],
                        "status": r["status"]
                    }
                    for r in records
                ]
            }

        return result

    async def get_user_trends(self, user_id: str):

        reports = await self.medical_repo.get_user_reports(
            user_id
        )

        grouped = self.extract_lab_history(reports)

        trends = self.build_trend_response(grouped)

        return {
            "user_id": user_id,
            "trends": trends
        }