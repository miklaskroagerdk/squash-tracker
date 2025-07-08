import os
import sys
import requests
import json

# Test the deployed application
url = "https://j6h5i7c1vpvo.manus.space/api/health"
response = requests.get(url)
print(f"Health check response: {response.status_code}")
print(response.json())

# Test the database status endpoint
url = "https://j6h5i7c1vpvo.manus.space/api/admin/database/status"
response = requests.get(url)
print(f"Database status response: {response.status_code}")
print(json.dumps(response.json(), indent=2))
