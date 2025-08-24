import os
import json
import pandas as pd

nist_dir = "./NIST"
excel_file = os.path.join(nist_dir, "compliance_all.xlsx")

all_data = []

# Loop through all JSON files in NIST folder
for file in os.listdir(nist_dir):
    if file.endswith(".json"):
        filepath = os.path.join(nist_dir, file)
        with open(filepath, "r") as f:
            data = json.load(f)
            # Ensure Device column exists
            if "Device" not in data:
                data["Device"] = file.replace(".json", "")
            all_data.append(data)

# Convert to DataFrame
df = pd.DataFrame(all_data)

# Save to Excel
df.to_excel(excel_file, index=False)

print(f"✅ Excel summary saved to {excel_file}")
