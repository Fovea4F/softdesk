import requests

endpoint = 'http://127.0.0.1:8000/api/user'
response = requests.get(endpoint, json={'username': 'MartinS'})
print(response.json())
print(response.status_code)
