import sqlite3
import re

# Database connection setup
def get_connection():
    """
    Establishes and returns a connection to the SQLite database.
    """
    return sqlite3.connect('Data/PreProcessed/Agent_Project25.db')

class RAGAgent:
    def __init__(self):
        """
        Initializes the RAGAgent with a database connection.
        """
        self.conn = get_connection()

    def generate_response(self, query):
        """
        Handles general queries and fetches relevant data from the database based on keywords.
        """
        try:
            query_lower = query.lower()
            if "fundamentals" in query_lower:
                return self.fetch_fundamentals(query)
            elif "insider" in query_lower:
                return self.fetch_insider_transactions(query)
            elif "option" in query_lower or "option activities" in query_lower:
                return self.fetch_options_activity(query)
            elif "price" in query_lower:
                return self.fetch_price_data(query)
            elif "news" in query_lower or "article" in query_lower:
                return self.fetch_news(query)
            else:
                return "❓ Sorry, I couldn't understand the query. Please be more specific."
        except Exception as e:
            return f"⚠️ An error occurred: {e}"

    def extract_ticker_and_timespan(self, query):
        """
        Extracts the ticker symbol enclosed in parentheses and the time span (days, months, years) from the user's query.
        """
        # Extract ticker from parentheses
        ticker_match = re.search(r'\(([^)]+)\)', query)
        ticker = ticker_match.group(1).upper() if ticker_match else None

        # Extract time span
        days_match = re.search(r'(\d+)\s*days', query)
        months_match = re.search(r'(\d+)\s*months', query)
        years_match = re.search(r'(\d+)\s*years', query)

        if days_match:
            timespan = int(days_match.group(1))
        elif months_match:
            timespan = int(months_match.group(1)) * 30  # Approximate month length
        elif years_match:
            timespan = int(years_match.group(1)) * 365  # Approximate year length
        else:
            timespan = 30  # Default to 30 days if not specified

        return ticker, timespan

    def fetch_price_data(self, query):
        """
        Fetches price data filtered by ticker and date range.
        """
        cursor = self.conn.cursor()
        ticker, timespan = self.extract_ticker_and_timespan(query)

        if ticker:
            sql_query = f"""
                SELECT Date, Open, High, Low, Close, Volume, Ticker
                FROM Price_Data
                WHERE Ticker = ?
                ORDER BY Date DESC
                LIMIT ?
            """
            cursor.execute(sql_query, (ticker, timespan))
        else:
            return "❌ No ticker found in the query."

        data = cursor.fetchall()

        if data:
            return data
        else:
            return f"❌ No price data found for {ticker}."

    # Other Data Retrieval Methods
    def fetch_fundamentals(self, query):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Fundamentals LIMIT 5")
        return cursor.fetchall()

    def fetch_insider_transactions(self, query):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Insider_Transactions LIMIT 5")
        return cursor.fetchall()

    def fetch_options_activity(self, query):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Options_Contracts LIMIT 5")
        return cursor.fetchall()

    def fetch_news(self, query):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Articles LIMIT 5")
        return cursor.fetchall()

if __name__ == "__main__":
    agent = RAGAgent()
    while True:
        user_input = input(">> Enter your query (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        response = agent.generate_response(user_input)
        print(response)
