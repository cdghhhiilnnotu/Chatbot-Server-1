import requests

url = "http://127.0.0.1:1237/response/2055010051"

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

queries = [
    "Dương thích ai?",
]

for query in queries:
    print(query)
    test_with(query)
    print("\n")

# print(requests.get('"http://127.0.0.1:1237/login/a"').json())

# import requests

# response = requests.get("http://127.0.0.1:1237/login/2055010051")
# print(response.json())