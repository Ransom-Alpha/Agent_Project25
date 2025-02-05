import pandas as pd
import os

# Folder containing the price data CSV files
price_folder = 'data/Price/'  # Update this path if different
preprocessed_folder = 'data/PreProcessed/'  # Folder to save preprocessed files

# Ensure the preprocessed folder exists
os.makedirs(preprocessed_folder, exist_ok=True)

# List to store combined data
all_price_data = []

# Function to process each price file
def process_price_file(file_path, ticker):
    df = pd.read_csv(file_path)
    
    # Add ticker information
    df['ticker'] = ticker

    # Standardize date format
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', utc=True).dt.normalize()

    # Ensure numeric columns are correctly typed
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# Process all CSV files in the folder
for filename in os.listdir(price_folder):
    if filename.endswith('.csv') and filename.endswith('_data.csv'):
        file_path = os.path.join(price_folder, filename)

        # Extract ticker from the filename (assuming format "TICKER_data.csv")
        ticker = filename.replace('_data.csv', '')

        # Process the file and append data
        processed_df = process_price_file(file_path, ticker)
        all_price_data.append(processed_df)

# Combine all processed data into a single DataFrame
combined_df = pd.concat(all_price_data, ignore_index=True)

# Save the combined price data for Neo4j import
combined_df.to_csv(os.path.join(preprocessed_folder, 'combined_price_data.csv'), index=False)

# Create Ticker-Price Relationships for Neo4j
relationships_df = combined_df[['ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
relationships_df.to_csv(os.path.join(preprocessed_folder, 'ticker_price_relationships.csv'), index=False)

print("✅ Preprocessing complete! Files saved in the PreProcessed folder for Neo4j import.")
