import sys
sys.path.append('../../../demo-5')

from modules.rags import BaseRAG

class FAISSRag(BaseRAG):

    def __init__(self, db_vector):
        super().__init__(db_vector)

    def retrieving(self, query:str, limit:int=3):
        return self.db.as_retriever(search_kwargs={"k": limit}).invoke(query)

    def to_text(self, query:str):
        docs = self.retrieving(query=query)
        texts = []
        
        for doc in docs:
            texts.append(doc.page_content.strip())
        
        return '\n'.join(texts)
    
if __name__ == "__main__":
    from modules.storings import FAISSDatabase
    from modules.embeddings import HFEmbedding
    import pickle
    
    with open('../../chunks.pkl', "rb") as file:
        chunks = pickle.load(file)

    embedding = HFEmbedding()
    vdb = FAISSDatabase(embedding, '../storings/sources/database/faiss/v0')

    question = "Học phần là gì?"

    rag = FAISSRag(vdb)

    context = rag.to_text(question)

    print(context)
