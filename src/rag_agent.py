import sqlite3
from src.database import get_connection

class RAGAgent:
    def __init__(self):
        self.conn = get_connection()

    def generate_response(self, query):
        """
        Handles general queries and fetches relevant data from the database.
        """
        try:
            # Check for keywords to determine the type of data to retrieve
            if "fundamentals" in query.lower():
                return self.fetch_fundamentals(query)
            elif "insider" in query.lower():
                return self.fetch_insider_transactions(query)
            elif "options" in query.lower():
                return self.fetch_options_activity(query)
            elif "price" in query.lower():
                return self.fetch_price_data(query)
            else:
                return "❓ Sorry, I couldn't understand the query. Please be more specific."
        except Exception as e:
            return f"⚠️ An error occurred: {e}"

    def fetch_fundamentals(self, query):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Fundamentals LIMIT 5")  # Example query
        data = cursor.fetchall()
        return f"📊 Fundamentals (Sample Data):\n{data}"

    def fetch_insider_transactions(self, query):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Insider_Transactions LIMIT 5")
        data = cursor.fetchall()
        return f"📈 Insider Transactions (Sample Data):\n{data}"

    def fetch_options_activity(self, query):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Options_Contracts LIMIT 5")
        data = cursor.fetchall()
        return f"📈 Options Activity (Sample Data):\n{data}"

    def fetch_price_data(self, query):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Price_Data LIMIT 5")
        data = cursor.fetchall()
        return f"📈 Price Data (Sample Data):\n{data}"

# For testing
if __name__ == "__main__":
    agent = RAGAgent()
    print(agent.generate_response("Show me fundamentals"))
