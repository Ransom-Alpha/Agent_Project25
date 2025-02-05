import pandas as pd
import os

# Folder containing the daily options activity files
options_folder = 'Data/Unusual_Options/'  # Update this path if different
preprocessed_folder = 'Data/PreProcessed/'  # Folder to save preprocessed files

# Ensure the preprocessed folder exists
os.makedirs(preprocessed_folder, exist_ok=True)

# List to store combined data
all_data = []

# Function to clean and process each file
def process_options_file(file_path, file_date):
    df = pd.read_csv(file_path)
    
    # Standardize column names
    if 'Price~' in df.columns:
        df.rename(columns={'Price~': 'Price'}, inplace=True)

    # Clean percentage fields (IV)
    if 'IV' in df.columns:
        df['IV'] = df['IV'].astype(str).str.replace('%', '', regex=False)
        df['IV'] = pd.to_numeric(df['IV'], errors='coerce')

    # Convert date fields
    if 'Exp Date' in df.columns:
        df['Exp Date'] = pd.to_datetime(df['Exp Date'], errors='coerce')
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

    # Add date from filename if not present
    df['date'] = file_date

    return df

# Process all CSV files in the folder
for filename in os.listdir(options_folder):
    if filename.endswith('.csv') and filename.startswith('Unusual-Stock-Options-Activity-'):
        file_path = os.path.join(options_folder, filename)

        # Extract date from filename
        file_date = filename.split('-')[-1].replace('.csv', '')
        file_date = pd.to_datetime(file_date, errors='coerce')

        # Process the file and append data
        processed_df = process_options_file(file_path, file_date)
        all_data.append(processed_df)

# Combine all processed data into a single DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Export the combined data for Neo4j import
combined_df.to_csv(os.path.join(preprocessed_folder, 'combined_options_contracts.csv'), index=False)

# Create relationships between Tickers and Option Contracts
relationships_df = combined_df[['Symbol', 'date', 'Exp Date', 'Type', 'Strike', 'Volume', 'Open Int', 'Vol/OI', 'IV', 'Delta']]
relationships_df.rename(columns={'Symbol': 'ticker'}, inplace=True)

# Save relationships for Neo4j
relationships_df.to_csv(os.path.join(preprocessed_folder, 'ticker_option_relationships.csv'), index=False)

print("✅ Preprocessing complete! Files saved in the PreProcessed folder for Neo4j import.")
