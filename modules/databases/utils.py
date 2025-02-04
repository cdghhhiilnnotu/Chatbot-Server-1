import string
import random
import streamlit_authenticator as stauth


def generate_random_string(length=10): 
    all_characters = string.ascii_letters + string.digits + string.punctuation 
    random_string = ''.join(random.choice(all_characters) for _ in range(length)) 
    return random_string

def hashing_password(passwords):
    hash_passwords = stauth.Hasher(passwords).generate()
    return passwords, hash_passwords