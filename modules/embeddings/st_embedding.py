import sys
sys.path.append('../../../demo-5')

from typing import List
from sentence_transformers import SentenceTransformer

from modules.embeddings import BaseEmbedding

from modules.configs import ST_EMBEDDING

class STEmbedding(BaseEmbedding):

    def __init__(self, model_name: str = ST_EMBEDDING):
        super().__init__('SentenceTransformer')
        self.core = SentenceTransformer(model_name)

    def encode(self, queries: List[str]):
        return self.core.encode(queries)
    
if __name__ == "__main__":
    st = STEmbedding()
    query = 'Học phần là gì?'
    embed_query = st.encode([query])
    print(embed_query.shape)
