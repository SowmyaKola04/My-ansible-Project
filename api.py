import requests

token = "1p3bGj4psffx7y8mnt9z6whmbxgpz8"
host = "http://172.31.1.227"

headers = {
    "Authorization": f"Bearer {token}"
}

# Disable SSL warnings (only for lab/testing)
requests.packages.urllib3.disable_warnings()

response = requests.get(f"{host}/api/v2/monitor/system/interface", headers=headers, verify=False)

if response.status_code == 200:
    print("[+] Success:", response.json())
else:
    print(f"[!] Failed: HTTP {response.status_code}")
    print(response.text)
