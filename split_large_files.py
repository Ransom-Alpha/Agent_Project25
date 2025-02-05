import os
import pandas as pd
import sqlite3
import math

def split_csv(file_path, max_size_mb=45):
    """Split a CSV file into smaller chunks."""
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Calculate number of chunks needed
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
    num_chunks = math.ceil(file_size / max_size_mb)
    chunk_size = len(df) // num_chunks
    
    # Create directory for chunks if it doesn't exist
    base_name = os.path.splitext(file_path)[0]
    chunks_dir = f"{base_name}_chunks"
    os.makedirs(chunks_dir, exist_ok=True)
    
    # Split and save chunks
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = None if i == num_chunks - 1 else (i + 1) * chunk_size
        chunk_df = df.iloc[start_idx:end_idx]
        chunk_path = os.path.join(chunks_dir, f"chunk_{i+1}.csv")
        chunk_df.to_csv(chunk_path, index=False)
    
    print(f"Split {file_path} into {num_chunks} chunks in {chunks_dir}")

def split_sqlite_db(db_path, max_size_mb=45):
    """Split a SQLite database into smaller chunks by table."""
    conn = sqlite3.connect(db_path)
    
    # Get list of tables
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Create directory for chunks
    base_name = os.path.splitext(db_path)[0]
    chunks_dir = f"{base_name}_chunks"
    os.makedirs(chunks_dir, exist_ok=True)
    
    # Export each table to CSV
    for table in tables:
        table_name = table[0]
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        
        # Split table if it's too large
        csv_path = os.path.join(chunks_dir, f"{table_name}.csv")
        df.to_csv(csv_path, index=False)
        
        if os.path.getsize(csv_path) > max_size_mb * 1024 * 1024:
            # If the CSV is too large, split it further
            split_csv(csv_path)
            os.remove(csv_path)  # Remove the original large CSV
    
    conn.close()
    print(f"Split database tables from {db_path} into CSV files in {chunks_dir}")

def main():
    # Split large CSV files
    csv_files = [
        "Data/PreProcessed/combined_insider_transactions.csv",
        "Data/PreProcessed/executive_ticker_relationships.csv"
    ]
    
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            split_csv(csv_file)
    
    # Split SQLite database
    db_file = "Data/PreProcessed/Agent_Project25.db"
    if os.path.exists(db_file):
        split_sqlite_db(db_file)

if __name__ == "__main__":
    main()
