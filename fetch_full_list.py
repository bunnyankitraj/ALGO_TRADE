import pandas as pd
import requests
import io
import os

# URL for Full Equity List
EQUITY_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

def get_master_list():
    """
    Fetches the Master Equity List from NSE and returns it as a DataFrame.
    """
    print("Fetching Full Equity list (EQUITY_L.csv)...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(EQUITY_URL, headers=headers)
        response.raise_for_status()
        
        # Read CSV
        df = pd.read_csv(io.StringIO(response.text))
        
        # Columns often have trailing spaces
        df.columns = [c.strip() for c in df.columns]
        
        # We need SYMBOL and NAME OF COMPANY
        df_clean = df[['SYMBOL', 'NAME OF COMPANY', 'ISIN NUMBER']].rename(columns={
            'SYMBOL': 'symbol',
            'NAME OF COMPANY': 'company_name',
            'ISIN NUMBER': 'isin'
        })
        
        print(f"Loaded {len(df_clean)} stocks from Master List.")
        return df_clean

    except Exception as e:
        print(f"Error fetching master list: {e}")
        return pd.DataFrame()

def fetch_and_store_full_list():
    # Deprecated for Firestore version, but keeping for compatibility if needed
    # (Though we removed the DB save logic from here to avoid dependency on the old db schema)
    print("Warning: fetch_and_store_full_list is deprecated in the Firestore architecture. Use get_master_list() in-memory.")
    return get_master_list()

if __name__ == "__main__":
    df = get_master_list()
    print(df.head())
