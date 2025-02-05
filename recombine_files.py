import os
import pandas as pd
import sqlite3
import glob

def recombine_csv_chunks(chunks_dir):
    """Recombine CSV chunks into a single file."""
    # Get all chunk files
    chunk_files = sorted(glob.glob(os.path.join(chunks_dir, "chunk_*.csv")))
    if not chunk_files:
        return
    
    # Read and combine chunks
    dfs = []
    for chunk_file in chunk_files:
        df = pd.read_csv(chunk_file)
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Save combined file
    output_path = os.path.dirname(chunks_dir)
    output_file = os.path.join(output_path, os.path.basename(chunks_dir)[:-7] + ".csv")
    combined_df.to_csv(output_file, index=False)
    print(f"Recombined chunks into {output_file}")

def recombine_db_chunks(chunks_dir):
    """Recombine database table chunks into a SQLite database."""
    # Create new database
    db_path = os.path.join(os.path.dirname(chunks_dir), "Agent_Project25.db")
    conn = sqlite3.connect(db_path)
    
    # Process each table's chunks
    table_files = glob.glob(os.path.join(chunks_dir, "*.csv"))
    table_chunks_dirs = glob.glob(os.path.join(chunks_dir, "*_chunks"))
    
    # Handle direct table files first
    for table_file in table_files:
        table_name = os.path.splitext(os.path.basename(table_file))[0]
        df = pd.read_csv(table_file)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Imported {table_name} into database")
    
    # Handle chunked tables
    for chunks_dir in table_chunks_dirs:
        table_name = os.path.basename(chunks_dir)[:-7]  # Remove '_chunks'
        chunk_files = sorted(glob.glob(os.path.join(chunks_dir, "chunk_*.csv")))
        
        if chunk_files:
            # Read and combine chunks
            dfs = []
            for chunk_file in chunk_files:
                df = pd.read_csv(chunk_file)
                dfs.append(df)
            
            combined_df = pd.concat(dfs, ignore_index=True)
            combined_df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Imported combined {table_name} chunks into database")
    
    conn.close()
    print(f"Recombined database at {db_path}")

def main():
    # Recombine CSV files
    csv_chunks = [
        "Data/PreProcessed/combined_insider_transactions_chunks",
        "Data/PreProcessed/executive_ticker_relationships_chunks"
    ]
    
    for chunks_dir in csv_chunks:
        if os.path.exists(chunks_dir):
            recombine_csv_chunks(chunks_dir)
    
    # Recombine database
    db_chunks = "Data/PreProcessed/Agent_Project25_chunks"
    if os.path.exists(db_chunks):
        recombine_db_chunks(db_chunks)

if __name__ == "__main__":
    main()
