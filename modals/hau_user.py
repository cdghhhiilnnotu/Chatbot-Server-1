from typing import Dict
import yaml

class HAUUser:
    def __init__(self, user_id: str = "", name: str = "", password: str = "", hashed_password: str = "", schechule: str = "", exam: str = "", chats: str = "", infor: Dict = {}):
        self.user_id = user_id
        self.name = name
        self.password = password
        self.hashed_password = hashed_password
        self.schechule = schechule
        self.exam = exam
        self.chats = chats
        self.infor = infor

    def __repr__(self):
        return (f"HAUUser(user_id={self.user_id}, name={self.name}, "
                f"password={self.password}, schechule={self.schechule}, "
                f"exam={self.exam}, chats={self.chats}, infor={self.infor})")

    def from_yaml(self, yaml_path: str):
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
        
        self.user_id = data.get('user_id', "")
        self.name = data[self.user_id].get('name', "")
        self.password = data[self.user_id].get('password', "")
        self.hashed_password = data[self.user_id].get('hashed_password', "")
        self.schechule = data[self.user_id].get('schechule', "")
        self.exam = data[self.user_id].get('exam', "")
        self.chats = data[self.user_id].get('chats', "")
        self.infor = data[self.user_id].get('infor', {})

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "password": self.password,
            "hashed_password": self.hashed_password,
            "schechule": self.schechule,
            "exam": self.exam,
            "chats": self.chats,
            "infor": self.infor
        }

    def to_yaml(self, yaml_path: str):
        """
        Save the HAUUser object's data to a YAML file.
        
        Args:
            yaml_path (str): Path to the YAML file where the data will be written.
        """
        data = {
            self.user_id: {
                "name": self.name,
                "password": self.password,
                "hashed_password": self.hashed_password,
                "schechule": self.schechule,
                "exam": self.exam,
                "chats": self.chats,
                "infor": self.infor,
            }
        }