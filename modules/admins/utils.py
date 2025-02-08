import os
import json
import streamlit as st
from datetime import datetime
import yaml
import pandas as pd
import random
import streamlit_authenticator as stauth
import string

from modules.configs import CHATS_PATH, CONFIG_ADMINS_PATH, ACCOUNTS_PATH
from modules.databases import HauAccDB

accounts_db = HauAccDB()
accounts_db.load_json([ACCOUNTS_PATH])

def load_chat_history(folder_path=CHATS_PATH):
    try:
        all_chats = {}
        for file in os.listdir(folder_path):
            if file.endswith('.json'):
                student_id = file.replace('.json', '')
                with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
                    all_chats[student_id] = json.load(f)
        return all_chats
    except FileNotFoundError:
        print("File not found!")
        return {}
    except Exception as e:
        print(e)
        return {}
    
def display_chat_messages(messages):
    for msg in messages:
        if msg["type"].lower() == "user":
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.write("👤 User:", msg["text"])
            with col2:
                st.write(msg["chat_at"])
        else:
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.write("🤖 Server:", msg["text"])
            with col2:
                st.write(msg["chat_at"])

def filter_chats_by_date(chat_data, start_date, end_date):
    filtered_chats = {}
    for chat_id, chat_info in chat_data.items():
        chat_date = datetime.strptime(chat_info['createdAt'], "%Y-%m-%d %H:%M:%S")
        if start_date <= chat_date.date() <= end_date:
            filtered_chats[chat_id] = chat_info
    return filtered_chats

def reset_state():
    st.session_state.chunks = []
    st.session_state.delete_index = None
    # st.session_state.updated_rag = False

def import_users(csv_file):
    df = pd.read_csv(csv_file, encoding='utf-8')
    data = df.to_json(orient="records", force_ascii=False)
    data = json.loads(data)
    users = {}
    for item in data:
        users[item[list(item.keys())[1]]] = {
            "name": item[list(item.keys())[0]],
            "password": item[list(item.keys())[2]],
            "role": item[list(item.keys())[3]],
            "others": "none"
        }
    return users

def setup_state():
    if "chunks" not in st.session_state:
        st.session_state.chunks = []

    if "delete_index" not in st.session_state:
        st.session_state.delete_index = None

    if "updated_rag" not in st.session_state:
        st.session_state.updated_rag = False

def add_account(new_users):
    return accounts_db.insert_acc(new_users)

def update_account(updated_user):
    return accounts_db.update_acc(updated_user)

def load_account(username):
    acc_infor = accounts_db.load_acc(username)
    username, name, role, password, org_password = username, acc_infor['name'], acc_infor['role'], acc_infor['hash_password'], acc_infor['password']

    return username, name, role, password, org_password

def delete_account(del_users):
    return accounts_db.delete_acc(del_users)

def load_accounts():
    usernames, names, roles, passwords, org_passwords, cookie_name, cookie_key, cookie_value, cookie_expiry_days = accounts_db.load_accs()

    return usernames, names, roles, passwords, org_passwords, cookie_name, cookie_key, cookie_value, cookie_expiry_days

def generate_random_string(length=10): 
    all_characters = string.ascii_letters + string.digits + string.punctuation 
    random_string = ''.join(random.choice(all_characters) for _ in range(length)) 
    return random_string


if __name__ == "__main__":
    print(import_users('data.csv'))