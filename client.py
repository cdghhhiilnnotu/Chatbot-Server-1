import requests

url = 'http://localhost:1237/response'
# s = requests.Session()
# # r = s.get(url, stream=True)

# for i in s.get(url, stream=True).iter_lines():
#     print(i, end="")

with requests.post(url, json={"query":"chao ban.", "username":"20", "history":[]},stream=True) as response:
    for line in response.iter_content():
        if line:  # Filter out keep-alive new lines
            print(line, end='')