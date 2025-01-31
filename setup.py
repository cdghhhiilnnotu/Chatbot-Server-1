from modules.chunkings import SemanticChunk
from modules.embeddings import HFEmbedding
from modules.storings import FAISSDatabase
from modules.extractings import DOCXExtractor, HTMLExtractor, PDFExtractor, TXTExtractor
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
        # for file in os.listdir(sub_dir):
        #     file_path = os.path.join(sub_dir, file)
    print(len(docs))
    embedding = HFEmbedding()    
    chunker = SemanticChunk(embedding_model=embedding)
    chunks = chunker.chunking(docs)

    with open(f'./database/faiss/v1/documents.pkl', "wb") as file:
        pickle.dump(chunks, file)

    embedding = HFEmbedding()
    vdb = FAISSDatabase(embedding, './database/faiss/v1')

    db = vdb.db_create(chunks=chunks)
    # extractor = PDFExtractor()
    # doc = extractor.load("D:/Works/DATN/Dataset/pdfs/Hướng dẫn thực hiện quy chế công tác sinh viên trong đào tạo đại học hệ chính quy theo hệ thống tín chỉ.pdf")
    # print(doc)
            

if __name__ == "__main__":
    get_chunk_from_dir('D:/Works/DATN/Dataset', ['docxs', 'htmls', 'pdfs'])
    

