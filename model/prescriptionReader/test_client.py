import requests

with open('pres1.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/extract', files=files)

print(response.json())
