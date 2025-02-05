import sqlite3
import os

def examine_database():
    db_path = os.path.join('Data', 'PreProcessed', 'Agent_Project25.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\n=== Database Tables ===")
    for table in tables:
        table_name = table[0]
        print(f"\n--- Table: {table_name} ---")
        
        # Get schema for table
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print("\nSchema:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Get sample rows
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        rows = cursor.fetchall()
        if rows:
            print("\nSample Data:")
            for row in rows:
                print(f"  {row}")

    conn.close()

if __name__ == "__main__":
    examine_database()
