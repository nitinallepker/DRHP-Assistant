import os
import json
import fitz  # PyMuPDF
import pandas as pd
import docx
from typing import Dict, Any, List, Union

class DocumentExtractor:
    """
    DocumentExtractor reads different file formats (PDF, Excel, DOCX, JSON)
    and extracts their text and tabular data into a structured format.
    """

    def extract_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text from a PDF file page-by-page using PyMuPDF (fitz).
        """
        pages = []
        doc = fitz.open(file_path)
        for idx, page in enumerate(doc):
            text = page.get_text()
            pages.append({
                "page_number": idx + 1,
                "text": text.strip()
            })
        doc.close()
        return pages

    def extract_docx(self, file_path: str) -> str:
        """
        Extracts paragraph text from a Word document (.docx) using python-docx.
        """
        doc = docx.Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    def extract_excel(self, file_path: str) -> Dict[str, str]:
        """
        Extracts sheet tables from an Excel file, converting each sheet to a Markdown table.
        """
        sheets = {}
        with pd.ExcelFile(file_path) as excel_file:
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                # Fill NaN values with empty string for clean markdown tables
                df_clean = df.fillna("")
                sheets[sheet_name] = df_clean.to_markdown(index=False)
        return sheets

    def extract_json(self, file_path: str) -> Dict[str, Any]:
        """
        Loads and returns parsed content from a JSON configuration file.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def extract(self, file_path: str, file_extension: str) -> Union[List[Dict[str, Any]], Dict[str, Any], str]:
        """
        Routes the file to the appropriate extraction method based on its extension.
        """
        ext = file_extension.lower()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at '{file_path}'")
            
        if ext == ".pdf":
            return self.extract_pdf(file_path)
        elif ext in [".xlsx", ".xls"]:
            return self.extract_excel(file_path)
        elif ext in [".docx", ".doc"]:
            return self.extract_docx(file_path)
        elif ext == ".json":
            return self.extract_json(file_path)
        else:
            # Fallback to plain text read
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                raise ValueError(f"Extraction failed: Unsupported file extension '{ext}'")
