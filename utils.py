import yaml
import json

from modules.configs import CHATS_PATH, CONFIG_USERS_PATH, ACCOUNTS_PATH

# with open(CONFIG_USERS_PATH, "r", encoding="utf-8") as file:
#     accounts_data = yaml.safe_load(file)
from modules.databases import HauAccDB

accounts_db = HauAccDB()
accounts_db.load_json([ACCOUNTS_PATH])

LLM_NAME = 'llama3.2'
EMBEDDING_MODEL = 'keepitreal/vietnamese-sbert'

def get_history(history_messages):
    his = []
    for item in history_messages:
        his.append({
            "type": item['type'],
            "text": item['text']
        })
    return his

def load_account(username):
    try:
        acc_infor = accounts_db.load_acc(username)
        data = {
            'username' : username,
            'name' : acc_infor['name'],
            'password' : acc_infor['password'],
            'others' : acc_infor['others']
        }
    except Exception as e:
        data = {
            'error': str(e)
        }
    return data

def load_chats(username):
    json_path = f"{CHATS_PATH}/{username}.json"
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    return data

def load_query(queries, key_query):
    if key_query in queries:
        return queries.pop(key_query)
    return None


if __name__ == "__main__":
    print(load_chats('2051010032'))
    print(load_chats('2055010051'))
