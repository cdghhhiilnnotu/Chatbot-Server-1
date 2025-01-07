class BaseExtractor():
    name: str

    def __init__(self, name: str):
        self.name = name

    def load(self, pdf_path: str):
        raise NotImplementedError("The load from file method must be implemented by subclasses")

    def loads(self, pdfs_dir: str):
        raise NotImplementedError("The load from directory method must be implemented by subclasses")
    