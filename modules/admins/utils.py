import os
import json
import streamlit as st
from datetime import datetime
import yaml
import random
import streamlit_authenticator as stauth
import string

from modules.configs import CHATS_PATH, CONFIG_ADMINS_PATH

with open(CONFIG_ADMINS_PATH, "r", encoding="utf-8") as file:
    admins_data = yaml.safe_load(file)

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

def add_account(username, name, role, org_password):
    new_user = {
        "name": name,
        "role": role,
        "org_password": org_password,
        "password": "",
    }

    if username not in admins_data["credentials"]["usernames"]:
        admins_data["credentials"]["usernames"][username] = new_user

        update_yaml()
        return True
    else:
        return False
    
def update_yaml():
    credentials = admins_data['credentials']['usernames']
    usernames = list(credentials.keys())
    names = [info['name'] for info in credentials.values()]
    roles = [info['role'] for info in credentials.values()]
    org_passwords = [info['org_password'] for info in credentials.values()]

    cookie = admins_data['cookie']
    admins_data['cookie']['key'] = generate_random_string()

    passwords = stauth.Hasher(org_passwords).generate()
    for username, new_password in zip(usernames, passwords):
        credentials[username]['password'] = new_password

    with open(CONFIG_ADMINS_PATH, 'w', encoding='utf-8') as file:
        yaml.dump(admins_data, file, default_flow_style=False, allow_unicode=True)

def update_account(username, name, role, org_password):
    updated_user = {
        "name": name,
        "role": role,
        "org_password": org_password,
        "password": "",
    }

    if username in admins_data["credentials"]["usernames"] or username.lower() == "none":
        admins_data["credentials"]["usernames"][username] = updated_user

        update_yaml()
        return True
    else:
        return False

def load_account(username):
    usernames = admins_data['credentials']['usernames']
    username_infor = usernames[username]
    name = username_infor['name']
    role = username_infor['role']
    org_password = username_infor['org_password']
    password = username_infor['password']

    return username, name, role, password, org_password

def load_accounts():
    update_yaml()
    credentials = admins_data['credentials']['usernames']
    usernames = list(credentials.keys())
    names = [info['name'] for info in credentials.values()]
    roles = [info['role'] for info in credentials.values()]
    org_passwords = [info['org_password'] for info in credentials.values()]
    passwords = [info['password'] for info in credentials.values()]

    cookie = admins_data['cookie']
    cookie_name = cookie['name']
    cookie_key = cookie['key']
    cookie_value = cookie['value']
    cookie_expiry_days = cookie['expiry_days']

    return usernames, names, roles, passwords, org_passwords, cookie_name, cookie_key, cookie_value, cookie_expiry_days

def generate_random_string(length=10): 
    all_characters = string.ascii_letters + string.digits + string.punctuation 
    random_string = ''.join(random.choice(all_characters) for _ in range(length)) 
    return random_string