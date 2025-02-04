import yaml
import json

from modules.configs import CHATS_PATH, CONFIG_USERS_PATH

with open(CONFIG_USERS_PATH, "r", encoding="utf-8") as file:
    accounts_data = yaml.safe_load(file)

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
    users = accounts_data['usernames']

    try:
        user_infor = users[username]
        name = user_infor['name']
        password = user_infor['password']
        others = user_infor['others']

        data = {
            'username': username,
            'name': name,
            'password': password,
            'others': others,
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

if __name__ == "__main__":
    print(load_chats('2051010032'))
    print(load_chats('2055010051'))
