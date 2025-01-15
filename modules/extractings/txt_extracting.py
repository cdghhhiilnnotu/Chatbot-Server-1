import sys
sys.path.append('../../../demo-5')

import os
from langchain_core.documents import Document

from modules.extractings import BaseExtractor


class TXTExtractor(BaseExtractor):
    def __init__(self):
        super().__init__('TXTExtractor')

    def load(self, txt_path):
        try:
            txt_path = os.path.abspath(txt_path)
            with open(txt_path, "r", encoding="utf-8") as file:
                content = file.read()

            if not content.strip():
                raise ValueError("No content found in the CSV file.")

            # Create a Document instance
            document = Document(
                page_content=content,
                metadata={
                    "source": txt_path,
                    "hyperlinks": [],  
                    "tables": [],  
                    "error": ""
                }
            )
            return document

        except Exception as e:
            error_message = str(e)
            print(f"Error processing {os.path.basename(txt_path)}: {error_message}")
            return Document(
                page_content="",
                metadata={
                    "source": txt_path,
                    "hyperlinks": [],  
                    "tables": [],  
                    "error": error_message
                }
            )

    def loads(self, csv_dir):
        documents = []
        for csv_file in os.listdir(csv_dir):
            if csv_file.endswith(".csv"):
                txt_path = os.path.join(csv_dir, csv_file)
                documents.append(self.load(txt_path))
        return documents