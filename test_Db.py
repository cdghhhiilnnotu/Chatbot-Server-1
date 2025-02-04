from modules.databases import HauAccDB

from modules.configs import CONFIG_ADMINS_PATH, CONFIG_USERS_PATH
haudb = HauAccDB()
# haudb.load_yamls([CONFIG_ADMINS_PATH, CONFIG_USERS_PATH])
haudb.load_json(['./database/jsons/accounts.json'])

# print("Add")
# haudb.insert_acc({
#     'username1':{
#                 "name": "Quản trị viên 1",
#                 "password": "adminchatbot1",
#                 "role": "Admin",
#                 "others": "none"
#             },
#     'username2':{
#                 "name": "Quản trị viên 1",
#                 "password": "adminchatbot1",
#                 "role": "Admin",
#                 "others": "none"
#             },
# })
# print("Delete")
# haudb.delete_acc('username2')
# print("Update")
# haudb.update_acc({
#     'username1':{
#                 "name": "Nguyễn Trần Mai Ảnh",
#                 "password": "adminchatbot1",
#                 "role": "Admin",
#                 "others": "none"
#             },
# })
# print("View")
# print(haudb.load_acc('username1'))

usernames, names, roles, passwords, org_passwords, cookie_name, cookie_key, cookie_value, cookie_expiry_days = haudb.load_accs()

# print(usernames)
# print(names)
# print(roles)
# print(passwords)
# print(org_passwords)
# print(cookie_name)
# print(cookie_key)
# print(cookie_value)
# print(cookie_expiry_days)