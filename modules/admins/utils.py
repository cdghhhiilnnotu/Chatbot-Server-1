import os
import json
import streamlit as st
from datetime import datetime
import yaml
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
    st.session_state.updated_rag = True

def setup_state():
    if "chunks" not in st.session_state:
        st.session_state.chunks = []

    if "delete_index" not in st.session_state:
        st.session_state.delete_index = None

    if "updated_rag" not in st.session_state:
        st.session_state.updated_rag = False

def add_account(username, name, role, org_password, others = "none"):
    new_user = {
        username : {
            "name": name,
            "role": role,
            "password": org_password,
            "others": others
        }
    }

    if accounts_db.insert_acc(new_user) == "":
        return True
    else:
        return False

def update_account(username, name, role, org_password, others = "none"):
    updated_user = {
        username : {
            "name": name,
            "role": role,
            "password": org_password,
            "others": others
        }
    }

    if accounts_db.update_acc(updated_user) == "":
        return True
    else:
        return False

def load_account(username):
    acc_infor = accounts_db.load_acc(username)
    username, name, role, password, org_password = username, acc_infor['name'], acc_infor['role'], acc_infor['hash_password'], acc_infor['password']

    return username, name, role, password, org_password

def delete_account(username):
    if accounts_db.delete_acc(username):
        return True
    else:
        return False

def load_accounts():
    usernames, names, roles, passwords, org_passwords, cookie_name, cookie_key, cookie_value, cookie_expiry_days = accounts_db.load_accs()

    return usernames, names, roles, passwords, org_passwords, cookie_name, cookie_key, cookie_value, cookie_expiry_days

def generate_random_string(length=10): 
    all_characters = string.ascii_letters + string.digits + string.punctuation 
    random_string = ''.join(random.choice(all_characters) for _ in range(length)) 
    return random_string