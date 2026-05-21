import pdfplumber
import fitz
from typing import List
import camelot


class PDFTool:

    @staticmethod
    def extract_pages(file_path: str) -> List[str]:
        pages = []

        # -----------------------------
        # Try pdfplumber (best quality)
        # -----------------------------
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    pages.append(text.strip())

        except Exception as e:
            print(f"pdfplumber failed: {e}")

        # -----------------------------
        # Fallback: PyMuPDF (fitz)
        # -----------------------------
        if not any(pages):  # if all pages empty
            pages = []
            try:
                with fitz.open(file_path) as doc:
                    for page in doc:
                        text = page.get_text() or ""
                        pages.append(text.strip())
            except Exception as e:
                print(f"PyMuPDF failed: {e}")

        return pages

    @staticmethod
    def extract_tables(file_path: str) -> List[dict]:
        def is_single_value_row(row) -> bool:
                    values = [str(x).strip() for x in row if str(x).strip() != ""]
                    return len(values) <= 1
            
        # extract tables
        tables = camelot.read_pdf(file_path, pages="all")

        labs = []
        # raw_tables = []
        # for i, table in enumerate(tables):
        #     df = table.df
        #     raw_tables.append(df.to_dict(orient="records"))
            
        for table in tables:
            df = table.df

            for i in range(len(df)):

                row = df.iloc[i].tolist()
                # print("Processing row:", row)

                if len(row) < 3:
                    continue
                if is_single_value_row(row):
                    continue

                test_name = row[0].strip()
                result = row[1].strip()
                reference= row[3].strip()
                units= row[4].strip()

                # extract number
                import re
                match = re.search(r'([\d.]+)', result)
                if not match:
                    continue

                value = float(match.group(1))

                # detect status from remarks column
                status = "NORMAL"
                if "H" in result or "**H" in result:
                    status = "HIGH"

                labs.append({
                    "test-name": test_name,
                    "value": value,
                    "reference": reference,
                    "units": units,
                    "status": status
                })

        return labs