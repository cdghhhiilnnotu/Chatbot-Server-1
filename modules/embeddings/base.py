from typing import List


class BaseEmbedding():
    name: str

    def __init__(self, name: str):
        self.name = name

    def encode(self, inputs: List[str]):
        raise NotImplementedError("The encode method must be implemented by subclasses")

