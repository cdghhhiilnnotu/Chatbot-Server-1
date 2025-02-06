import requests

url = "http://127.0.0.1:1237/login"

def test_with(query=""):
    with requests.post(
        url,
        json={
            "query": query,
            "chat_id": "anh"
        },
        stream=True
    ) as response:
        # Print HTTP response status code
        print(f"Status Code: {response.status_code}")
        
        # Print HTTP headers
        print("Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        # Print JSON response body if available
        try:
            print("JSON Response:")
            print(response.json())
        except ValueError:
            print("Response is not in JSON format.")
        
        # Print raw content line by line if streaming
        print("Raw Content:")
        for line in response.iter_content():
            if line:  # Exclude keep-alive new lines
                print(line, end='')

# queries = [
#     "Chào bạn, tôi tên là Dương, tên bạn là gì?",
#     "Tên tôi là gì?",
#     "Học phần là gì?",
#     "Hủy đăng kí lớp học phần có mã tín chỉ TH4309 của sinh viên có mã sinh viên là 2055010153.",
#     "Đăng kí lớp học phần có mã tín chỉ TH4309 của sinh viên có mã sinh viên là 2055010051.",
#     "Tra cứu lịch thi của sinh viên có mã 2055010051 của ngày 03/02/2023.",
#     "Tra cứu lịch học của sinh viên có mã 2055010051 ngày 04/09/2023.",
# ]
# for query in queries:
#     print(query)
#     test_with(query)
#     print("\n")

# print(requests.get('"http://127.0.0.1:1237/login/a"').json())

# import requests

response = requests.get("http://127.0.0.1:1237/login/2055010051")
print(response.json())

with requests.post(
        url,
        json={
            "username": '2055010051',
            "password": 'duong1'
        }
    ) as response:
        # Print HTTP response status code
        print(f"Status Code: {response.status_code}")
        
        # Print HTTP headers
        print("Headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        print("JSON Response:")
        print(response.json())