import os
import sys
import json
import pandas as pd

def json_to_excel(input_folder, output_file):
    rows = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                    rows.append(data)
    df = pd.DataFrame(rows)
    df.to_excel(output_file, index=False)
    print(f"Inventory saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 json_to_excel.py <input_folder> <output_file>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_file = sys.argv[2]
    json_to_excel(input_folder, output_file)
