import sys
import requests
import pyperclip
from plyer import notification


if len(sys.argv) != 2:
	print("Usage: python example_client.py <file_path>")
	sys.exit(1)

file_path = sys.argv[1]

url = "https://img.luxferre.dev/upload"

headers = {'X-API-KEY': "secret_key"}

with open(file_path, "rb") as file:
	files = {"file": file}
	response = requests.post(url, files=files, headers=headers)

if response.status_code == 201:
	response_json = response.json()
	upload_url = response_json.get('url', 'No URL in response')
	notification_text = f"Copied to clipboard.\n\n {upload_url}"
	notification_title = "Upload successful"
	pyperclip.copy(upload_url)
else:
	notification_text = "Unknown error"
	notification_title = "Upload Unsuccessful"

notification.notify(
    title=notification_title,
    message=notification_text,
    timeout=10
)
