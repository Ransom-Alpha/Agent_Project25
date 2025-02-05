import pandas as pd
import yfinance as yf
import os
from datetime import datetime

# Read tickers from the CSV file
tickers_df = pd.read_csv(r"C:\Users\Jrans\Desktop\AI Project\SubFiles\News_Tickers.csv")
tickers = tickers_df['Symbol'].dropna().unique()

# List of fundamental factors to download
factors = [
    'sector', 'recommendationKey', 'targetMeanPrice', 'targetMedianPrice',
    'targetHighPrice', 'targetLowPrice', 'fiftyDayAverage', 'twoHundredDayAverage',
    'pegRatio', 'forwardPE', 'trailingPE', 'enterpriseToEbitda',
    'returnOnAssets', 'returnOnEquity', 'grossMargins', 'ebitdaMargins', 'profitMargins'
]

# Directory to save the CSV file
output_dir = r"C:\Users\Jrans\Desktop\AI Project\Hdata\Fundamentals"
os.makedirs(output_dir, exist_ok=True)

# Get today's date for the output file name
today_date = datetime.now().strftime("%Y-%m-%d")
output_path = os.path.join(output_dir, f"{today_date}.csv")

# Collect data for all tickers
fundamental_data = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info_data = stock.info

        # Extract relevant factors
        data = {'Ticker': ticker}
        for factor in factors:
            data[factor] = info_data.get(factor, None)

        fundamental_data.append(data)

        print(f"Fundamental data for {ticker} retrieved successfully.")

    except Exception as e:
        print(f"Failed to retrieve data for {ticker}: {e}")

# Save the collected data to a CSV file
fundamentals_df = pd.DataFrame(fundamental_data)
fundamentals_df.to_csv(output_path, index=False)

print(f"All fundamental data saved to {output_path}")
