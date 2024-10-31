import requests
import json


url = 'http://0.0.0.0:8080/control'

# Command to move the robot forward
data = {
    "rtc_topic": "rt/api/sport/request",
    "api_id": 1008,
    "optional_param": json.dumps({"x": 0.5, "y": 0, "z": 0})
}

# Send the POST request
response = requests.post(url, json=data)

# Print the response from the server
print("Response Status Code:", response.status_code)
print("Response Body:", response.text)