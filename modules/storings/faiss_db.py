import sys
sys.path.append('../../../demo-5')

import faiss
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

from modules.storings import BaseDatabase


class FAISSDatabase(BaseDatabase):

    db_name = 'faiss/'

    def __init__(self, embedding_model, db_path:str='faiss/'):
        super().__init__(embedding_model, db_path)

    def db_create(self, chunks):
        sentences = [chunk.page_content for chunk in chunks]
        embeddings = self.embedding_model.encode(sentences)
        embeddings_array = np.array(embeddings)

        d = embeddings_array.shape[1]

        index = faiss.IndexFlatL2(d)
        index.add(embeddings_array)

        docstore = InMemoryDocstore(
            {i: doc for i, doc in enumerate(chunks)}
        )

        index_to_docstore_id = {i: i for i in range(len(chunks))}

        self.db = FAISS(
            embedding_function=self.embedding_model.core,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )
        self.db.save_local(self.db_path)
        print(f"Database saved in {self.db_path}")
        return self.db
    
    def db_get(self):
        self.db = FAISS.load_local(self.db_path, embeddings=self.embedding_model.core, allow_dangerous_deserialization=True)
        return self.db
        
    def db_add(self, docs):
        ids = [len(self.db.index_to_docstore_id) + i for i in range(len(docs))]
        self.db.add_documents(documents=docs, ids=ids)

    def db_len(self):
        return len(self.db.index_to_docstore_id)

if __name__ == "__main__":
    from modules.embeddings import HFEmbedding
    import pickle
    # Load documents from pickle file
    with open('../../chunks.pkl', "rb") as file:
        chunks = pickle.load(file)

    embedding = HFEmbedding()
    vdb = FAISSDatabase(embedding)

    db = vdb.db_create(chunks=chunks)
    print(db)

    question = "Học phần là gì?"

    retrieved_docs = db.as_retriever(search_kwargs={"k": 3}).invoke(question)

    print(retrieved_docs)

    db1 = vdb.db_get()

    question = "Học phần là gì?"

    retrieved_docs = db1.as_retriever(search_kwargs={"k": 3}).invoke(question)

    print(retrieved_docs)

