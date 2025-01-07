import requests

url = 'https://6cf3-35-204-82-190.ngrok-free.app/response'
# s = requests.Session()
# # r = s.get(url, stream=True)

# for i in s.get(url, stream=True).iter_lines():
#     print(i, end="")

with requests.post(url, json={"query":"Hãy hủy học phần có mã tín chỉ TH4309 của sinh viên có mã sinh viên 2055010051."},stream=True) as response:
    for line in response.iter_content():
        if line:  # Filter out keep-alive new lines
            print(line, end='')