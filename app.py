import streamlit as st
import streamlit_authenticator as stauth
from streamlit_cookies_controller import CookieController

from modules.admins import run_page, load_accounts

def main():
    usernames, names, roles, passwords, org_password, cookie_name, cookie_key, cookie_value, cookie_expiry_days = load_accounts()

    controller = CookieController()
    controller.set(name=cookie_name, value=cookie_value)

    authenticator = stauth.Authenticate(
        names,
        usernames,
        passwords,
        cookie_name,
        cookie_key,
        cookie_expiry_days
    )
    name, authentication_status, username = authenticator.login("Đăng nhập", "main")
    try:
        user_index = usernames.index(username)
    except:
        pass

    if authentication_status == False:
        st.error("Tài khoản/Mật khẩu sai!")

    if authentication_status:
        run_page(usernames[user_index], roles[user_index])
        authenticator.logout("Đăng xuất", "sidebar")



if __name__ == "__main__":
    main()
