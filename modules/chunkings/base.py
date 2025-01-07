from typing import List
from langchain_core.documents import Document


class BaseChunk():
    name: str

    def __init__(self, name):
        self.name = name

    def chunk(self, documents: List[Document | str]):
        raise NotImplementedError("The chunk method must be implemented by subclasses")
