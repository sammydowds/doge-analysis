import os
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from datetime import date 
import json

import json

def append_to_json(file_path, data):
    try:
        with open(file_path, 'r+') as file:
            file_data = json.load(file)
            if isinstance(file_data, list):
                file_data.append(data)
            else:
                print(f"Unsupported JSON format in {file_path}. Cannot append data.")
                return
            file.seek(0)
            json.dump(file_data, file, indent=4)
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            json.dump([data], file, indent=4)
    except json.JSONDecodeError:
        with open(file_path, 'w') as file:
            json.dump([data], file, indent=4)

def format_currency(amount):
    return "${:.2f}M".format(round(amount / 1_000_000))


def analyze_html(path, key, estimated_savings):
    with open(path, "r") as file:
        html = file.read()
        soup = BeautifulSoup(html, "html.parser")
        today = date.today() 
    
        # extract tables - note, read_html fails without isolating table html first 
        tables = soup.find_all("table")
        contracts_table, leases_table = tables
        for a in contracts_table.find_all('a'):
            a.replace_with(a["href"])
        
        # create dataframes
        contracts = pd.read_html(StringIO(str(contracts_table)))[0]
        leases = pd.read_html(StringIO(str(leases_table)))[0]
        
        # convert key (column) to numbers and filter out non-dollar strings
        contracts = contracts[contracts[key].str.contains(r'\$', na=False)]
        leases = leases[leases[key].str.contains(r'\$', na=False)]
        contracts[key] = contracts[key].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        leases[key] = leases[key].replace({r'\$': '', ',': ''}, regex=True).astype(float)
        contracts[f'Formatted {key}'] = contracts[key].apply(format_currency)

        # meta
        contracts_with_zero_value = (contracts[key] == 0).sum()
        contract_total = contracts[key].sum()
        leases_total = leases[key].sum()
        total_value = contract_total + leases_total

        meta = {
            'created': str(today),
            'key': key,
            'total_contracts': len(contracts),
            'total_leases': len(leases),
            'contracts_sum': round(contract_total, 2),
            'leases_sum': round(leases_total, 2),
            'total': round(contract_total + leases_total, 2),
            'percent_of_estimated_savings': round((total_value / estimated_savings) * 100, 2),
            'contract_as_percent_of_estimated_savings': round((contract_total / estimated_savings) * 100, 2),
            'lease_as_percent_of_estimated_savings': round((leases_total / estimated_savings) * 100, 2),
            'contracts_with_zero_value': str(contracts_with_zero_value)
        }
       
        # sort
        all_leases = leases.sort_values(by=key, ascending=False).to_dict(orient='records')
        all_contracts = contracts.sort_values(by=key, ascending=False).to_dict(orient='records')
        
        # write
        output_dir = f'./{today}-{key.upper()}'
        os.makedirs(output_dir, exist_ok=True)
        with open(f'{output_dir}/doge_receipts.json', 'w') as fp:
            json.dump(meta, fp)
        with open(f'{output_dir}/contracts.json', 'w', encoding='utf-8') as f:
            json.dump(all_contracts, f, indent=4)
        with open(f'{output_dir}/leases.json', 'w', encoding='utf-8') as f:
            json.dump(all_leases, f, indent=4)

        # compound data
        append_to_json("savings_data.json", meta)