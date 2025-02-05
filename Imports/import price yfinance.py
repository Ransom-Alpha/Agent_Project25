import pandas as pd
import yfinance as yf
import os

# Read tickers from the CSV file
tickers_df = pd.read_csv(r"C:\Users\Jrans\Desktop\AI Project\SubFiles\News_Tickers.csv")
tickers = tickers_df['Symbol'].dropna().unique()

# Define the date range
start_date = '2019-02-01'
end_date = '2024-02-01'

# Directory to save the CSV files
output_dir = r"C:\Users\Jrans\Desktop\AI Project\Hdata\Price"
os.makedirs(output_dir, exist_ok=True)

# Download daily price data (Open, High, Low, Close, Volume) for each ticker and save to separate CSV files
for ticker in tickers:
    try:
        # Download historical data
        stock = yf.Ticker(ticker)
        hist_data = stock.history(start=start_date, end=end_date)

        # Filter to include only the desired columns
        final_data = hist_data[['Open', 'High', 'Low', 'Close', 'Volume']]

        # Save to CSV
        output_path = os.path.join(output_dir, f"{ticker}_data.csv")
        final_data.to_csv(output_path)

        print(f"Data for {ticker} saved successfully.")

    except Exception as e:
        print(f"Failed to process {ticker}: {e}")
