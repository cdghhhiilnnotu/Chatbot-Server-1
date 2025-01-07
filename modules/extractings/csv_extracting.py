import sys
sys.path.append('../../../demo-5')

import os
import pandas as pd
from langchain_core.documents import Document

from modules.extractings import BaseExtractor


class CSVExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()

    def load(self, csv_path):
        try:
            csv_path = os.path.abspath(csv_path)
            df = pd.read_csv(csv_path)
            content = df.to_string(index=False)

            if not content.strip():
                raise ValueError("No content found in the CSV file.")

            # Create a Document instance
            document = Document(
                page_content=content,
                metadata={
                    "source": csv_path,
                    "hyperlinks": [],  
                    "tables": [],  
                    "error": ""
                }
            )
            return document

        except Exception as e:
            error_message = str(e)
            print(f"Error processing {os.path.basename(csv_path)}: {error_message}")
            return Document(
                page_content="",
                metadata={
                    "source": csv_path,
                    "hyperlinks": [],  
                    "tables": [],  
                    "error": error_message
                }
            )

    def loads(self, csv_dir):
        documents = []
        for csv_file in os.listdir(csv_dir):
            if csv_file.endswith(".csv"):
                csv_path = os.path.join(csv_dir, csv_file)
                documents.append(self.load(csv_path))
        return documents