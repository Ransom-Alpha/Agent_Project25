import sqlite3
import os

# Path to the SQLite database file
DB_PATH = os.path.join('Data', 'PreProcessed', 'Agent_Project25.db')

def get_connection():
    """
    Establishes a connection to the SQLite database.
    Returns:
        conn (sqlite3.Connection): SQLite database connection object.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"❌ Database connection error: {e}")
        return None
