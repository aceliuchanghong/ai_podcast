import requests

# python client.py
response = requests.post("http://127.0.0.1:21500/predict", json={"input": 4.0})
print(f"Status: {response.status_code}\nResponse:\n {response.text}")
