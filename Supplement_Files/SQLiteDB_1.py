import sqlite3
import os

# Path to the SQLite database
db_path = os.path.join('Data', 'PreProcessed', 'Agent_Project25.db')

# Connect to the database (creates the file if it doesn't exist)
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Test: Create a simple table (you'll replace this with actual data later)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Test (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("✅ SQLite database created successfully at:", db_path)
