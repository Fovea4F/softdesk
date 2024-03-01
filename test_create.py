import requests

endpoint = 'http://127.0.0.1:8000/api/user/create'
response = requests.post(endpoint, json={'email': 'MartinL', })
print(response.json())
print(response.status_code)
