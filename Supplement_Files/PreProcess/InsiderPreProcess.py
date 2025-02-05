import pandas as pd
import os
import json

# Folder containing the insider transaction JSON files
insider_folder = 'data/InsiderTran/'  # Update this path if different
preprocessed_folder = 'data/PreProcessed/'  # Folder to save preprocessed files

# Ensure the preprocessed folder exists
os.makedirs(preprocessed_folder, exist_ok=True)

# List to store combined data
all_transactions = []

# Process all JSON files in the folder
for filename in os.listdir(insider_folder):
    if filename.endswith('.json'):
        file_path = os.path.join(insider_folder, filename)

        with open(file_path, 'r') as file:
            data = json.load(file)

            # Extract ticker from the filename (assuming it's the ticker)
            ticker = filename.replace('_insider_transactions.json', '')

            for transaction in data:
                transaction['ticker'] = ticker  # Add ticker to each transaction
                all_transactions.append(transaction)

# Convert to DataFrame
transactions_df = pd.DataFrame(all_transactions)

# Data Cleaning
transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'], errors='coerce')
transactions_df['shares'] = pd.to_numeric(transactions_df['shares'], errors='coerce')
transactions_df['share_price'] = pd.to_numeric(transactions_df['share_price'], errors='coerce')

# Create unique transaction ID
transactions_df['transaction_id'] = transactions_df.apply(lambda row: f"{row['ticker']}_{row['transaction_date']}_{row.name}", axis=1)

# Save the combined transactions file
transactions_df.to_csv(os.path.join(preprocessed_folder, 'combined_insider_transactions.csv'), index=False)

# Create Executive-Ticker Relationships for Neo4j
relationships_df = transactions_df[['transaction_id', 'ticker', 'executive', 'executive_title', 'transaction_date']]
relationships_df.to_csv(os.path.join(preprocessed_folder, 'executive_ticker_relationships.csv'), index=False)

print("✅ Preprocessing complete! Files saved in the PreProcessed folder for Neo4j import.")
