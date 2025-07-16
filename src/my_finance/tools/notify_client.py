import requests

url = "https://api.day.app/push"
headers = {
    'Content-Type': 'application/json; charset=utf-8'
}

DEVICE_KEY = "d4CSZvfz5P2VL5pdo62QYY"


def send_notification(title, content):
    data = {
        "body": content,
        "title": title,
        "device_key": DEVICE_KEY
    }
    requests.post(url, headers=headers, json=data)
