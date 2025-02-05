import sqlite3
import pandas as pd
import os

# Path to the database
db_path = os.path.join('Data', 'PreProcessed', 'Agent_Project25.db')

# Connect to SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Folder containing preprocessed files
preprocessed_folder = os.path.join('Data', 'PreProcessed')

# List of files to import
files = {
    'articles.csv': 'Articles',
    'article_ticker_relationships.csv': 'Article_Ticker_Relationships',
    'article_topic_relationships.csv': 'Article_Topic_Relationships',
    'combined_insider_transactions.csv': 'Insider_Transactions',
    'executive_ticker_relationships.csv': 'Executive_Ticker_Relationships',
    'combined_options_contracts.csv': 'Options_Contracts',
    'ticker_option_relationships.csv': 'Ticker_Option_Relationships',
    'combined_price_data.csv': 'Price_Data',
    'ticker_price_relationships.csv': 'Ticker_Price_Relationships',
    'preprocessed_2025-02-04.csv': 'Fundamentals'
}

# Function to import each CSV into SQLite
def import_csv_to_sqlite(file_path, table_name):
    df = pd.read_csv(file_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"✅ Imported {file_path} into {table_name}")

# Import each file
for file_name, table_name in files.items():
    file_path = os.path.join(preprocessed_folder, file_name)
    if os.path.exists(file_path):
        import_csv_to_sqlite(file_path, table_name)
    else:
        print(f"⚠️ File not found: {file_path}")

# Close the connection
conn.close()

print("🚀 All preprocessed data imported successfully into SQLite!")
