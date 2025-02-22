import requests

def infer_postgresql_tye(value):
    if isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    elif isinstance(value, str):
        return "TEXT"
    elif isinstance(value, bool):
        return "BOOLEAN"
    elif isinstance(value, list) or isinstance(value, dict):
        return "JSONB"
    else:
        return "TEXT"

def get_schema_from_api(api_url):
    response = requests.get(api_url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from API: {response.status_code}")
    data = response.json()
    if not data:
        raise Exception("No data found in the API response")
    first_entry = data[0]
    schema = {col: infer_postgresql_tye(value) for col, value in first_entry.items()}
    
    print("Suggested PSQL Table schema:")
    for col, col_type in schema.items():
        print(f"{col}: {col_type}")
    return 

# api_endpoint = 'http://rest.nbaapi.com/api/playerdatatotals/name/Lamelo%20Ball'
# get_schema_from_api(api_endpoint)
    


