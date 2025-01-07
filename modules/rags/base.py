class BaseRAG():

    def __init__(self, db_vector):
        self.db_vector = db_vector
        self.db = db_vector.db_get()

    def retrieving(self, query:str, limit:int=3):
        raise NotImplementedError("The retrieving method must be implemented by subclasses")
