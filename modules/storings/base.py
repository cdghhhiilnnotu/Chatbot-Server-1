import os
from typing import List


class BaseDatabase():
    
    db_dir = './sources/database/'
    db_name = 'base/'
    
    def __init__(self, embedding_model, db_path:str='base/'):
        if db_path == self.db_name:
            os.makedirs(self.db_dir+self.db_name, exist_ok=True)
            db_version = len(os.listdir(self.db_dir+self.db_name))
            db_path = self.db_dir+self.db_name+f'v{db_version}/'
            os.makedirs(db_path, exist_ok=True)
        else:
            os.makedirs(db_path, exist_ok=True)
        self.embedding_model = embedding_model
        self.db_path = db_path
        
    def db_create(self, docs: List):
        raise NotImplementedError("The create method must be implemented by subclasses")

    def db_get(self, db_path: str):
        raise NotImplementedError("The get method must be implemented by subclasses")

    def db_add(self, docs: List):
        raise NotImplementedError("The add method must be implemented by subclasses")
    
    def db_delete(self, docs: List):
        raise NotImplementedError("The delete method must be implemented by subclasses")



