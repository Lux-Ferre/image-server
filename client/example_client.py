import requests


url = "http://127.0.0.1:5000/upload"
file_path = "image.png"

headers = {'X-API-KEY': "secret_key"}

with open(file_path, "rb") as file:
	files = {"file": file}
	response = requests.post(url, files=files, headers=headers)
	print(response.json())

