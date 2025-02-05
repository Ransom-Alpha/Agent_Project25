import requests
import json
import time
import os
import pandas as pd
from datetime import datetime

# Alpha Vantage API key
API_KEY = 'HI5ADT0RWWANGUID'

# Base URL for the Alpha Vantage insider transactions API
BASE_URL = 'https://www.alphavantage.co/query'

# Path to the CSV file containing S&P 500 tickers
TICKERS_CSV_PATH = r"C:\Users\Jrans\Desktop\AI Project\SubFiles\News_Tickers.csv"

# Directory to save individual insider transactions
OUTPUT_DIR = r"C:\Users\Jrans\Desktop\AI Project\Hdata\InsiderTran"

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read the tickers from the CSV file
try:
    sp500_tickers_df = pd.read_csv(TICKERS_CSV_PATH)
    sp500_tickers = sp500_tickers_df['Symbol'].dropna().unique().tolist()
    print(f"Loaded {len(sp500_tickers)} tickers from the CSV file.")
except Exception as e:
    print(f"Error reading tickers CSV file: {e}")
    sp500_tickers = []

# Function to fetch insider transactions for a given ticker
def fetch_insider_transactions(symbol):
    """
    Fetches insider transactions for a specific company symbol.

    Parameters:
        symbol (str): The ticker symbol of the company.

    Returns:
        list: A list containing the insider transactions.
    """
    formatted_symbol = symbol.replace('.', '-')

    params = {
        'function': 'INSIDER_TRANSACTIONS',
        'symbol': formatted_symbol,
        'apikey': API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Debug print to inspect API response structure
        print(f"API response for {symbol}: {json.dumps(data, indent=4)}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for {symbol}: {http_err}")
        return []
    except requests.exceptions.Timeout:
        print(f"Request timed out for {symbol}")
        return []
    except Exception as err:
        print(f"Error occurred for {symbol}: {err}")
        return []

    # Adjust the key based on actual API response structure
    transactions = data.get('transactions') or data.get('data') or data.get('insiderTransactions', [])

    # Debug print to verify extracted transactions
    print(f"Extracted transactions for {symbol}: {transactions}")

    if not transactions:
        print(f"No transactions for {symbol}. Full API response: {json.dumps(data, indent=4)}")

    return transactions

# Loop through each ticker and fetch insider transactions
for index, ticker in enumerate(sp500_tickers):
    print(f"Processing {ticker} ({index + 1}/{len(sp500_tickers)})...")
    transactions_data = fetch_insider_transactions(ticker)

    if isinstance(transactions_data, list) and len(transactions_data) > 0:
        output_path = os.path.join(OUTPUT_DIR, f"{ticker}_insider_transactions.json")
        try:
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(transactions_data, json_file, ensure_ascii=False, indent=4)
            print(f"Successfully saved insider transactions for {ticker} at {output_path}.")
        except Exception as save_err:
            print(f"Error saving file for {ticker}: {save_err}")
    else:
        print(f"No data to save for {ticker}.")

    # Throttle API requests to avoid exceeding rate limits
    time.sleep(12)  # 5 requests per minute = 12 seconds between requests
