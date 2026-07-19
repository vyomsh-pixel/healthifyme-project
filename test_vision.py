import requests
import base64

# test 404 vs 200
try:
    res = requests.post("http://localhost:8001/api/analyze-food", json={"image": "dummy_base_64"})
    print("Status:", res.status_code)
    print("Response:", res.text)
except Exception as e:
    print("Error:", e)
