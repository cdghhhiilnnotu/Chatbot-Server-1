from typing import Dict
import yaml

class HAUAdmin:
    def __init__(self, username: str = "", name: str = "", password: str = "", hashed_password: str = "", role: str = "Viewer"):
        if role not in ["Admin", "Viewer"]:
            raise ValueError("Role must be either 'Admin' or 'Viewer'")
        
        self.username = username
        self.name = name
        self.password = password
        self.hashed_password = hashed_password
        self.role = role

    def __repr__(self):
        return (f"HAUAdmin(username={self.username}, name={self.name}, "
                f"password={self.password}, role={self.role})")

    def from_yaml(self, yaml_path: str):
        with open(yaml_path, 'r') as file:
            data = yaml.safe_load(file)
        
        self.username = data.get('username', "")
        self.name = data[self.username].get('name', "")
        self.password = data[self.username].get('password', "")
        self.hashed_password = data[self.username].get('hashed_password', "")
        self.role = data[self.username].get('role', "Viewer")
        if self.role not in ["Admin", "Viewer"]:
            raise ValueError("Role must be either 'Admin' or 'Viewer'")

    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "name": self.name,
            "password": self.password,
            "hashed_password": self.hashed_password,
            "role": self.role
        }

    def to_yaml(self, yaml_path: str):
        """
        Save the HAUAdmin object's data to a YAML file.
        
        Args:
            yaml_path (str): Path to the YAML file where the data will be written.
        """
        data = {
            self.username: {
                "name": self.name,
                "password": self.password,
                "hashed_password": self.hashed_password,
                "role": self.role,
            }
        }
