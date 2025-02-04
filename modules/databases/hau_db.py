import yaml
from typing import List, Dict
import json
from modules.databases import BaseDB
from modules.databases.utils import generate_random_string, hashing_password
import os
from pathlib import Path

class HauAccDB(BaseDB):

    def __init__(self, db_path="./database/jsons/accounts.json"):
        super().__init__("HauDatabase")
        self.data = {
            'cookie': {},
            'credentials': {
                'usernames': {}
            }
        }
        os.makedirs(Path(db_path).parent, exist_ok=True)
        self.db_path = db_path

    def load_yamls(self, yamls_list: List):
        for yaml_path in yamls_list:
            with open(yaml_path, "r", encoding="utf-8") as file:
                yaml_data = yaml.safe_load(file)
                self.data['cookie'] = yaml_data['cookie']

                for username in yaml_data['credentials']['usernames'].keys():
                    self.data['credentials']['usernames'][username] = yaml_data['credentials']['usernames'][username]

        self.update_db()
        
    def delete_acc(self, username: str):
        self.data['credentials']['usernames'].pop(username, None)
        self.update_db()

    def load_acc(self, username: str):
        if username not in self.data['credentials']['usernames'].keys():
            print(f"Key {username} does NOT exist.")
            return {}
        else:
            return self.data['credentials']['usernames'][username]

    def insert_acc(self, accs: Dict[str, Dict]):
        """
        accs = {
            "username1": {
                ...
            },
            "username2": {
                ...
            }
        }
        """
        for acc in accs:
            if acc not in self.data['credentials']['usernames'].keys():
                self.data['credentials']['usernames'][acc] = accs[acc]
            else:
                print(f"Key {acc} ALREADY exists.")
                continue
        self.update_db()

    def update_acc(self, accs: Dict[str, Dict]):
        """
        accs = {
            "username1": {
                ...
            },
            "username2": {
                ...
            }
        }
        """
        for acc in accs:
            if acc in self.data['credentials']['usernames'].keys():
                self.data['credentials']['usernames'][acc] = accs[acc]
            else:
                print(f"Key {acc} does NOT exist.")
                continue
        self.update_db()

    def load_json(self, jsons_list: List):
        for json_path in jsons_list:
            with open(json_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                self.data['cookie'] = json_data['cookie']

                for username in json_data['credentials']['usernames'].keys():
                    self.data['credentials']['usernames'][username] = json_data['credentials']['usernames'][username]

        self.update_db()

    def load_accs(self):
        users = self.data['credentials']['usernames']
        usernames = list(users.keys())
        names = [info['name'] for info in users.values()]
        roles = [info['role'] for info in users.values()]
        org_passwords = [info['password'] for info in users.values()]
        passwords = [info['hash_password'] for info in users.values()]

        cookie = self.data['cookie']
        cookie_name = cookie['name']
        cookie_key = cookie['key']
        cookie_value = cookie['value']
        cookie_expiry_days = cookie['expiry_days']

        return usernames, names, roles, passwords, org_passwords, cookie_name, cookie_key, cookie_value, cookie_expiry_days

    def update_db(self):
        self.data['cookie']['key'] = generate_random_string()
        passwords = []
        for user in self.data['credentials']['usernames'].keys():
            passwords.append(self.data['credentials']['usernames'][user]['password'])

        passwords, hashed = hashing_password(passwords)
        for user_idx, user in enumerate(self.data['credentials']['usernames'].keys()):
            self.data['credentials']['usernames'][user]['hash_password'] = hashed[user_idx]
        with open(self.db_path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False)


if __name__ == "__main__":
    from modules.configs import CONFIG_ADMINS_PATH
    haudb = HauAccDB()
    haudb.load_yamls([CONFIG_ADMINS_PATH])
