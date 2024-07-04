# --- src/data_manager.py ---
import os
import pandas as pd
from unstructured.partition.pdf import partition_pdf

# ... (Other imports)

class DataManager:
    """Loads and preprocesses data from various formats."""

    def __init__(self, file_path=None, file_content=None):
        """Initializes DataManager with either file path or file content."""
        self.file_path = file_path
        self.file_content = file_content

    def load_data(self, data_format="excel", sheet_name=None):
        """Loads data based on the specified format."""
        if self.file_path:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found: {self.file_path}")

            if data_format == "excel":
                return self._load_excel_data(sheet_name)
            elif data_format == "pdf":
                return self._load_pdf_data_unstructured()
            else:
                raise ValueError(f"Unsupported data format: {data_format}")
        elif self.file_content:
            if data_format == "pdf":
                return self._load_pdf_data_unstructured(from_content=True)
            else:
                raise ValueError(f"Unsupported data format for file content: {data_format}")
        else:
            raise ValueError("Either file_path or file_content must be provided.")

    def _load_excel_data(self, sheet_name=None):
        """Loads tabular data from an Excel file."""
        try:
            return pd.read_excel(self.file_path, sheet_name=sheet_name)
        except Exception as e:
            raise IOError(f"Error loading Excel data: {e}")

    def _load_pdf_data_unstructured(self, from_content=False):
        """Loads and extracts text from a PDF file using unstructured."""
        try:
            if from_content:
                elements = partition_pdf(filename=None, file=self.file_content)
            else:
                elements = partition_pdf(filename=self.file_path)

            extracted_text = ""
            for element in elements:
                if hasattr(element, "text"):
                    extracted_text += element.text + "\n"
            return extracted_text
        except Exception as e:
            raise IOError(f"Error loading PDF data: {e}")