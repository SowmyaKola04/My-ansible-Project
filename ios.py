import json
import re
import pandas as pd

with open("playbook_output.json", "r") as f:
    raw = f.read()

# Replace unescaped control characters (\r, \n, etc.) inside JSON
clean = re.sub(r'[\x00-\x1F]+', ' ', raw)

data = json.loads(clean)

# Ensure list format
if isinstance(data, dict):
    data = [data]

df = pd.DataFrame(data)

df = df[[ 
    "device",
    "old_version",
    "new_version",
    "old_memory",
    "new_memory",
    "old_uptime",
    "new_uptime",
    "flash_free_before",
    "flash_after_copy"
]]

output_file = "ios_upgrade_report.xlsx"
df.to_excel(output_file, index=False)

print(f"[✔] Report generated: {output_file}")
