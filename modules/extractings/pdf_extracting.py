import sys
sys.path.append('../../../demo-5')

import os
import fitz
import pytesseract
from pdf2image import convert_from_path
from langchain_core.documents import Document

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSEREACT_EXE')

from modules.extractings import BaseExtractor


class PDFExtractor(BaseExtractor):
    def __init__(self):
        super().__init__('PDFExtractor')

    def load(self, pdf_path):
        pdf_path = os.path.abspath(pdf_path)
        try:
            doc = fitz.open(pdf_path)
            pdf_text = ""
            hyperlinks = []
            
            for page in doc:
                pdf_text += page.get_text()
                links = page.get_links()
                if links:
                    for link in links:
                        if "uri" in link:
                            hyperlinks.append(link["uri"])
            
            if not pdf_text.strip():
                images = convert_from_path(pdf_path)
                ocr_text = ""
                for image in images:
                    ocr_text += pytesseract.image_to_string(image, lang="vie")
                pdf_text = ocr_text
            
            if not pdf_text.strip():
                raise ValueError("No content found in the PDF.")
            
            document = Document(
                page_content=pdf_text,
                metadata={
                    "source": pdf_path,
                    "hyperlinks": hyperlinks,  
                    "tables": [],  
                    "error": ""
                }
            )
            return document

        except Exception as e:
            error_message = str(e)
            print(f"Error processing {pdf_path}: {error_message}")
            return Document(
                page_content="",
                metadata={
                    "source": pdf_path,
                    "hyperlinks": [],
                    "tables": [],
                    "error": error_message
                }
            )

    def loads(self, pdfs_dir):
        documents = []
        for pdf_file in os.listdir(pdfs_dir):
            if pdf_file.endswith(".pdf"):
                pdf_path = os.path.join(pdfs_dir, pdf_file)
                documents.append(self.load(pdf_path))
        return documents
    
if __name__ == '__main__':
    pdf_extractor = PDFExtractor()
    doc = pdf_extractor.load('../../sources/working/quyche.pdf')

    print(doc)
