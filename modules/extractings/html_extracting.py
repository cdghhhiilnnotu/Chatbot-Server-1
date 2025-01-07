import sys
sys.path.append('../../../demo-5')

import os
import pandas as pd
from bs4 import BeautifulSoup
from langchain_core.documents import Document

from modules.extractings import BaseExtractor


class HTMLExtractor(BaseExtractor):
    def __init__(self):
        super().__init__()

    def load(self, html_path):
        try:
            html_path = os.path.abspath(html_path)
            with open(html_path, 'r', encoding='utf-8') as file:
                res_cont = file.read()

            soup = BeautifulSoup(res_cont, "html.parser")

            title_div = soup.find("div", class_="col-md-12")
            title = title_div.get_text(strip=True) if title_div else "No title found"

            content_div = soup.find("div", class_="col-md-10 col-md-offset-1")
            content = content_div.get_text(strip=True) if content_div else "No content found"

            hyperlinks = []
            if content_div:
                for a_tag in content_div.find_all("a", href=True):
                    hyperlinks.append(a_tag['href'])

            table = soup.find("table")
            if table:
                df = pd.read_html(str(table))[0]
                table_text = df.to_string(index=False)
                content += "\n" + table_text + "\n"

            # Create a Document instance
            document = Document(
                page_content=content,
                metadata={
                    "source": html_path,
                    "hyperlinks": hyperlinks,  
                    "tables": [],  
                    "error": ""
                }
            )
            return document

        except Exception as e:
            error_message = str(e)
            print(f"Error processing {os.path.basename(html_path)}: {error_message}")
            return Document(
                page_content="",
                metadata={
                    "source": html_path,
                    "hyperlinks": hyperlinks,  
                    "tables": [],  
                    "error": error_message
                }
            )

    def loads(self, csv_dir):
        documents = []
        for csv_file in os.listdir(csv_dir):
            if csv_file.endswith(".csv"):
                html_path = os.path.join(csv_dir, csv_file)
                documents.append(self.load(html_path))
        return documents