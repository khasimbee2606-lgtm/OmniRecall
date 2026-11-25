import requests

url = "http://127.0.0.1:5000/search"

data = {
    "query": "person"
}

response = requests.post(url, json=data)

print("\nStatus Code :", response.status_code)

print("\nSearch Results\n")

for image in response.json():

    print(image)