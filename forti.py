import requests
import openpyxl

# FortiGate details
FG_IP = "172.31.1.227"
API_TOKEN = "1p3bGj4psffx7y8mnt9z6whmbxgpz8"
VDOM = "root"

# Base URL
BASE_URL = f"https://{FG_IP}/api/v2/cmdb"

# Disable SSL warnings (only for lab)
requests.packages.urllib3.disable_warnings()

# Headers
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# Endpoints for hardening parameters (example set, you can expand to all 16)
ENDPOINTS = {
    "System Info": f"{BASE_URL}/system/global?vdom={VDOM}",
    "Admin Access": f"{BASE_URL}/system/admin?vdom={VDOM}",
    "System Time": f"{BASE_URL}/system/ntp?vdom={VDOM}",
    "Logging": f"{BASE_URL}/log/syslogd/setting?vdom={VDOM}",
    "Firmware": f"https://{FG_IP}/api/v2/monitor/system/firmware?vdom={VDOM}",
    "Interfaces": f"{BASE_URL}/system/interface?vdom={VDOM}"
}

# Create Excel workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "FortiGate Hardening"

# Add headers
ws.append(["Parameter", "API Endpoint", "Output"])

# Loop through endpoints
for param, url in ENDPOINTS.items():
    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        if response.status_code == 200:
            data = response.json()
            ws.append([param, url, str(data)])
        else:
            ws.append([param, url, f"Error {response.status_code}"])
    except Exception as e:
        ws.append([param, url, f"Exception: {e}"])

# Save Excel
excel_file = "fortigate_hardening_output.xlsx"
wb.save(excel_file)
print(f"[+] Report saved to {excel_file}")
