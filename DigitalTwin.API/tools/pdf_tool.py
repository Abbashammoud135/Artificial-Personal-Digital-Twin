import pdfplumber
from tools.base.ITool import BaseExtractorTool

class PDFExtractorTool(BaseExtractorTool):

    def extract(self, file_path: str):

        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text()

        return text