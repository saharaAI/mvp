# --- src/data_manager.py ---
import os
import pandas as pd 
import PyPDF2
# (Add other import statements for additional data formats if needed)

class DataManager:
    """Loads and preprocesses data from various formats."""

    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self, data_format="excel", sheet_name=None):
        """Loads data based on the specified format.

        Args:
            data_format (str, optional): The format of the data. Defaults to "excel".
            sheet_name (str, optional): The sheet name for Excel files. Defaults to None (loads the first sheet). 

        Returns:
            pandas.DataFrame: The loaded data as a DataFrame.
        """

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if data_format == "excel":
            return self._load_excel_data(sheet_name)
        elif data_format == "pdf":
            return self._load_pdf_data()
        else:
            raise ValueError(f"Unsupported data format: {data_format}")

    def _load_excel_data(self, sheet_name=None):
        """Loads tabular data from an Excel file.

        Args:
            sheet_name (str, optional): The sheet name to load. Defaults to None (loads the first sheet).

        Returns:
            pandas.DataFrame: The loaded data.
        """
        try:
            return pd.read_excel(self.file_path, sheet_name=sheet_name)
        except Exception as e:
            raise IOError(f"Error loading Excel data: {e}")

    def _load_pdf_data(self):
        """Loads and extracts text from a PDF file. 
           (Basic text extraction, you might need more advanced techniques)

        Returns:
            str: The extracted text from the PDF. 
        """
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                extracted_text = ""
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    extracted_text += page_text
                return extracted_text 
        except Exception as e:
            raise IOError(f"Error loading PDF data: {e}")