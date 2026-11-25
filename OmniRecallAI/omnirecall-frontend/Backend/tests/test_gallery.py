import requests

url = "http://127.0.0.1:5000/gallery"

response = requests.get(url)

print("Status Code :", response.status_code)

print()

for image in response.json():

    print(image)