import requests

url = "http://10.101.1.116:8000/kpis"
response = requests.get(url)
data = response.json()  # Si le format est JSON
print(data)