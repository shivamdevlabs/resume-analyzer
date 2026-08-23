import requests

url = "http://127.0.0.1:8000/api/download"
data = {"resume_text": "Sample resume text\nWith multiple lines\nJust for testing."}

try:
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    if response.status_code != 200:
        print("Response Text:", response.text)
    else:
        print("Success, received bytes:", len(response.content))
except Exception as e:
    print("Error:", e)
