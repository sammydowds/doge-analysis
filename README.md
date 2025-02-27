
# Analyzing Receipts - DOGE

## Info

Visit this [blog post](https://textabyss.com/us/doge) to learn more. 

## Getting Started

1. Go to DOGE[dot]gov
2. Select "Savings" toggle
3. Expand tables to render all data
4. Open devtools, copy the body element and save it to `doge_analysis/savings_doge.html`
5. Ensure you have poetry, then `poetry install && python doge_analysis/main.py`

## Output

### Folder

A folder will be output containing all sorted contracts, sorted leases, and meta data created. 

### Compound Data

An entry will be added to `savings_data.json` for each run.