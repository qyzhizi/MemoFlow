# -*- coding: utf-8 -*-
import requests
import json

url = "http://127.0.0.1:9000/v1/index/lzp?key=1"

payload = json.dumps({
  "body": "body_test"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)