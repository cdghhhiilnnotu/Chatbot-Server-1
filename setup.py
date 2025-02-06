from modules.chunkings import SemanticChunk
from modules.embeddings import HFEmbedding
from modules.storings import FAISSDatabase
from modules.extractings import DOCXExtractor, HTMLExtractor, PDFExtractor, TXTExtractor
from modules.configs import CONFIG_ADMINS_PATH, CONFIG_USERS_PATH
import pickle
from modules.configs import FAISS_PATH
import os

def get_chunk_from_dir(dir_name, sub_dirs):
    docs = []
    for sub in sub_dirs:
        sub_dir = os.path.join(dir_name, sub)
        if "pdf" in sub:
            extractor = PDFExtractor()
            for file in os.listdir(sub_dir):
                file_path = os.path.join(sub_dir, file)
                doc = extractor.load(file_path)
                docs.append(doc)
        elif "html" in sub:
            extractor = HTMLExtractor()
            for file in os.listdir(sub_dir):
                file_path = os.path.join(sub_dir, file)
                doc = extractor.load(file_path)
                docs.append(doc)
        elif "docx" in sub:
            extractor = DOCXExtractor()
            for file in os.listdir(sub_dir):
                file_path = os.path.join(sub_dir, file)
                doc = extractor.load(file_path)
                docs.append(doc)
        elif "txt" in sub:
            extractor = TXTExtractor()
            for file in os.listdir(sub_dir):
                file_path = os.path.join(sub_dir, file)
                doc = extractor.load(file_path)
                docs.append(doc)
        else:
            continue

    print(len(docs))
    embedding = HFEmbedding()    
    chunker = SemanticChunk(embedding_model=embedding)
    chunks = chunker.chunking(docs)

    with open(f'{FAISS_PATH}/documents.pkl', "wb") as file:
        pickle.dump(chunks, file)

    embedding = HFEmbedding()
    vdb = FAISSDatabase(embedding, f'{FAISS_PATH}')

    db = vdb.db_create(chunks=chunks)

from modules.databases import HauAccDB


if __name__ == "__main__":
    haudb = HauAccDB()
    haudb.load_yamls([CONFIG_ADMINS_PATH, CONFIG_USERS_PATH])
    # get_chunk_from_dir('D:/Works/DATN/Dataset', ['docxs', 'htmls', 'pdfs'])
    

