#!/usr/bin/env python3
import os, sys, json
import pandas as pd

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def flatten_to_df(data):
    if isinstance(data, dict) and 'ansible_facts' in data:
        data = data['ansible_facts']
    # Normalize/flatten whatever structure we have
    df = pd.json_normalize(data, sep='.')
    return df

def main(base_dir):
    sheets = {}
    summary_rows = []
    for dev in sorted(os.listdir(base_dir)):
        devdir = os.path.join(base_dir, dev)
        if not os.path.isdir(devdir):
            continue
        json_files = [f for f in os.listdir(devdir) if f.endswith('.json')]
        if not json_files:
            continue
        path = os.path.join(devdir, json_files[0])
        try:
            j = load_json(path)
        except Exception as e:
            print(f"Skipping {dev}: cannot load JSON ({e})")
            continue
        df = flatten_to_df(j)
        sheets[dev] = df
        # build a small summary row: try to pick some common fields if present
        row = {'device': dev}
        candidates = ['ansible_hostname', 'ansible_all_ipv4_addresses', 'default_ipv4.address',
                      'distribution', 'nodename', 'ansible_product_name', 'ansible_system_vendor',
                      'ansible_machine']
        for c in candidates:
            # find a column that contains the token c
            colmatch = [col for col in df.columns if (col == c) or col.endswith(c) or c in col]
            if colmatch:
                try:
                    row[c] = df.iloc[0][colmatch[0]]
                except Exception:
                    row[c] = None
        summary_rows.append(row)

    out = os.path.join(base_dir, 'inventory_summary.xlsx')
    with pd.ExcelWriter(out, engine='openpyxl') as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=safe_name, index=False)
        if summary_rows:
            pd.DataFrame(summary_rows).to_excel(writer, sheet_name='Summary', index=False)
    print('Wrote', out)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: json_to_excel.py <base_dir>')
        sys.exit(1)
    main(sys.argv[1])
