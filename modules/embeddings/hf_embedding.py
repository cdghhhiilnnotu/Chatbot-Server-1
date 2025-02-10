import sys
sys.path.append('../../../demo-5')

import numpy as np
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings

from modules.embeddings import BaseEmbedding

from modules.configs import EMBEDDING_MODEL

class HFEmbedding(BaseEmbedding):

    def __init__(self, model_name: str =EMBEDDING_MODEL):
        super().__init__('HuggingFace')
        self.core = HuggingFaceEmbeddings(model_name=model_name)

    def encode(self, queries: List[str]):
        return np.array(self.core.embed_documents(queries))
    
if __name__ == "__main__":
    hf = HFEmbedding()
    print(hf.name)
