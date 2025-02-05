import sqlite3
import re
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

# Load environment variables
load_dotenv()

# --- DATABASE CONNECTION ---
def get_connection():
    return sqlite3.connect('Data/PreProcessed/Agent_Project25.db')

# --- DEEPSEEK MODEL SETUP ---
llm = OllamaLLM(
    model="deepseek-r1:32b",
    temperature=0.1
)

# --- VECTOR STORE SETUP ---
embedding_model = OpenAIEmbeddings(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model="text-embedding-ada-002"
)

# Initialize FAISS
vector_store = FAISS.from_texts([""], embedding_model)

# --- RETRIEVAL QA CHAIN SETUP ---
# Create prompt template
prompt = ChatPromptTemplate.from_template("""Answer the following question based on the provided context:

{context}

Question: {input}

Answer the question concisely and accurately.""")

# Create document chain
document_chain = create_stuff_documents_chain(llm, prompt)

# Create retrieval chain
retriever = vector_store.as_retriever()
qa_chain = create_retrieval_chain(retriever, document_chain)

# --- RAG AGENT CLASS ---
class RAGAgent:
    def __init__(self):
        self.conn = get_connection()

    def generate_response(self, query):
        try:
            query_lower = query.lower()
            
            # More sophisticated pattern matching
            if re.search(r'(fundamental|valuation|pe ratio|margin|sector|target price)', query_lower):
                return self.fetch_fundamentals(query)
            elif re.search(r'(insider|executive|purchase|sale|buy|sell|transaction)', query_lower):
                return self.fetch_insider_transactions(query)
            elif re.search(r'(option|call|put|strike|expiry|volume|open interest|iv|delta)', query_lower):
                return self.fetch_options_activity(query)
            elif re.search(r'(price|chart|trend|movement|high|low|close)', query_lower):
                return self.fetch_price_data(query)
            elif re.search(r'(news|article|report|announcement|press release)', query_lower):
                return self.fetch_news(query)
            else:
                # Enhanced RAG response using combined data sources
                context = []
                
                # Get relevant news articles
                cursor = self.conn.cursor()
                cursor.execute("""
            SELECT a.title, a.summary 
            FROM Articles a
            WHERE a.time_published >= datetime('now', '-7 days')
            ORDER BY a.time_published DESC 
            LIMIT 5
                """)
                articles = cursor.fetchall()
                if articles:
                    context.extend([f"Recent News:\nTitle: {title}\nSummary: {summary}" 
                                  for title, summary in articles])
                
                # Extract potential ticker from query
                ticker_match = re.search(r'\(([^)]+)\)', query)
                if ticker_match:
                    ticker = ticker_match.group(1).upper()
                    
                    # Add fundamentals context
                    cursor.execute("""
                    SELECT sector, recommendationKey, targetMeanPrice
                    FROM Fundamentals 
                    WHERE Ticker = ? AND date = (SELECT MAX(date) FROM Fundamentals)
                    """, (ticker,))
                    fundamentals = cursor.fetchone()
                    if fundamentals:
                        context.append(f"Company Info:\nSector: {fundamentals[0]}\n"
                                     f"Recommendation: {fundamentals[1]}\n"
                                     f"Target Price: ${fundamentals[2]}")
                
                # Combine all context
                combined_context = "\n\n".join(context)
                
                # Use RAG with enhanced context
                return qa_chain.invoke({
                    "input": query,
                    "context": combined_context
                })["answer"]
                
        except Exception as e:
            return f"⚠️ Error: {str(e)}"

    # --- HELPER FUNCTIONS ---
    def fetch_price_data(self, query):
        cursor = self.conn.cursor()
        
        # Extract ticker and days
        words = query.split()
        ticker = None
        days = 3  # default to 3 days
        
        # First look for number of days
        for i, word in enumerate(words):
            if word.isdigit():
                days = int(word)
            # Look for common day phrases
            elif word.lower() in ['day', 'days']:
                prev_word = words[i-1] if i > 0 else None
                if prev_word and prev_word.isdigit():
                    days = int(prev_word)
        
        # Look for exact uppercase ticker matches
        # First try to find any word that's already in all caps
        for word in words:
            if word.isupper() and len(word) >= 2:  # Only check words that are already uppercase
                cursor.execute("SELECT 1 FROM Price_Data WHERE Ticker = ? LIMIT 1", (word,))
                if cursor.fetchone():
                    ticker = word
                    break
        
        if not ticker:
            return "❌ No valid ticker found in query. Please include a stock symbol in ALL CAPS (e.g., NVDA, AAPL)"
            
        sql = """
            SELECT 
                Date,
                printf('%.2f', Open) as Open,
                printf('%.2f', High) as High,
                printf('%.2f', Low) as Low,
                printf('%.2f', Close) as Close,
                Volume
            FROM Price_Data
            WHERE ticker = ?
            ORDER BY Date DESC
            LIMIT ?
        """
        
        try:
            cursor.execute(sql, (ticker, days))
            results = cursor.fetchall()
            
            if not results:
                return f"No price data found for {ticker}"
                
            # Create a formatted table
            headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            table = self.format_table(results, headers)
            
            # Analyze the data based on common price queries
            query_lower = query.lower()
            analysis = ""
            
            if "high" in query_lower:
                highest_price = max(float(row[2]) for row in results)  # High is index 2
                highest_date = next(row[0] for row in results if float(row[2]) == highest_price)
                analysis = f"\nAnalysis: The highest price was ${highest_price:.2f} on {highest_date}"
            elif "low" in query_lower:
                lowest_price = min(float(row[3]) for row in results)  # Low is index 3
                lowest_date = next(row[0] for row in results if float(row[3]) == lowest_price)
                analysis = f"\nAnalysis: The lowest price was ${lowest_price:.2f} on {lowest_date}"
            elif "close" in query_lower:
                latest_close = float(results[0][4])  # Close is index 4
                analysis = f"\nAnalysis: The most recent closing price was ${latest_close:.2f}"
            
            # Add summary and analysis
            summary = f"\nShowing last {days} days of price data for {ticker}"
            return table + analysis + summary
            
        except Exception as e:
            return f"Error fetching price data for {ticker}: {str(e)}"

    def fetch_fundamentals(self, query):
        cursor = self.conn.cursor()
        # Extract ticker from the query (e.g., "META" from "Fundamental META")
        ticker = query.split()[-1].strip().upper()
        
        sql = """
            SELECT Ticker, sector, recommendationKey, targetMeanPrice, 
                   forwardPE, trailingPE, returnOnEquity, profitMargins
            FROM Fundamentals
            WHERE date = (SELECT MAX(date) FROM Fundamentals)
            AND Ticker = ?
        """
        cursor.execute(sql, (ticker,))
        results = cursor.fetchall()
        
        if not results:
            return f"No fundamental data found for {ticker}"
            
        return self.format_results(results, "fundamentals")

    def fetch_insider_transactions(self, query):
        cursor = self.conn.cursor()
        ticker_match = re.search(r'\(([^)]+)\)', query)
        ticker = ticker_match.group(1).upper() if ticker_match else None
        
        sql = """
            SELECT transaction_date, ticker, executive, executive_title,
                   acquisition_or_disposal, shares, share_price
            FROM Insider_Transactions
            WHERE transaction_date >= date('now', '-90 days')
        """
        if ticker:
            sql += " AND ticker = ?"
            cursor.execute(sql, (ticker,))
        else:
            cursor.execute(sql)
        return self.format_results(cursor.fetchall(), "insider")

    def fetch_options_activity(self, query):
        cursor = self.conn.cursor()
        ticker_match = re.search(r'\(([^)]+)\)', query)
        ticker = ticker_match.group(1).upper() if ticker_match else None
        
        sql = """
            SELECT Symbol, Type, Strike, [Exp Date], Volume, [Open Int],
                   [Vol/OI], IV, Delta
            FROM Options_Contracts
            WHERE [Vol/OI] > 1.0  -- Filter for unusual activity
            AND Volume > 100
        """
        if ticker:
            sql += " AND Symbol = ?"
            cursor.execute(sql, (ticker,))
        else:
            cursor.execute(sql + " LIMIT 10")
        return self.format_results(cursor.fetchall(), "options")

    def fetch_news(self, query):
        cursor = self.conn.cursor()
        
        # Extract ticker and number of articles
        words = query.split()
        ticker = words[-1].strip().upper()
        
        # Look for number of articles requested
        num_articles = 5  # default
        for i, word in enumerate(words):
            if word.isdigit():
                num_articles = int(word)
                break
        
        # First verify the tables and columns exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND (name='articles' OR name='article_ticker_relationships')
        """)
        tables = cursor.fetchall()
        if len(tables) < 2:
            return f"Database schema error: Required tables not found"
        
        sql = """
            SELECT 
                COALESCE(a.time_published, 'N/A') as date,
                COALESCE(a.title, 'N/A') as title,
                COALESCE(a.summary, 'N/A') as summary,
                COALESCE(a.source, 'N/A') as source,
                COALESCE(a.overall_sentiment_label, 'N/A') as sentiment,
                COALESCE(atr.relevance_score, 0) as relevance
            FROM Articles a
            INNER JOIN Article_Ticker_Relationships atr ON a.article_id = atr.article_id
            WHERE atr.ticker = ?
            ORDER BY a.time_published DESC, atr.relevance_score DESC
            LIMIT ?
        """
        
        try:
            cursor.execute(sql, (ticker, num_articles))
            results = cursor.fetchall()
            
            if not results:
                return f"No recent news found for {ticker}"
                
            formatted_results = []
            for date, title, summary, source, sentiment, relevance in results:
                article = f"""
📅 Date: {date}
📰 Title: {title}
🔍 Source: {source}
💭 Sentiment: {sentiment}
📊 Relevance: {relevance:.2f if isinstance(relevance, float) else relevance}
📝 Summary: {summary}
{'=' * 80}"""
                formatted_results.append(article)
                
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error fetching news for {ticker}: {str(e)}"

    def format_results(self, data, query_type):
        if not data:
            return "No data found."
            
        if query_type == "fundamentals":
            return self.format_table(data, ['Ticker', 'Sector', 'Recommendation', 'Target Price', 
                                          'Forward P/E', 'Trailing P/E', 'ROE', 'Margins'])
        elif query_type == "insider":
            return self.format_table(data, ['Date', 'Ticker', 'Executive', 'Title', 
                                          'Type', 'Shares', 'Price'])
        elif query_type == "options":
            return self.format_table(data, ['Symbol', 'Type', 'Strike', 'Expiry', 
                                          'Volume', 'Open Int', 'Vol/OI', 'IV', 'Delta'])
        return str(data)

    def format_table(self, data, headers):
        # Simple ASCII table formatting
        if not data:
            return "No data available"
            
        # Convert all data to strings and handle None values
        str_data = [[str(cell) if cell is not None else 'N/A' for cell in row] for row in data]
        
        # Get column widths
        widths = [max(len(str(x)) for x in col) for col in zip(headers, *str_data)]
        widths = [max(w, len(h)) for w, h in zip(widths, headers)]
        
        # Create separator line
        separator = '+' + '+'.join('-' * (w + 2) for w in widths) + '+'
        
        # Format header
        header = '|' + '|'.join(f' {h:<{w}} ' for w, h in zip(widths, headers)) + '|'
        
        # Format rows
        rows = []
        for row in str_data:
            rows.append('|' + '|'.join(f' {cell:<{w}} ' for w, cell in zip(widths, row)) + '|')
        
        # Combine all parts
        table = [separator, header, separator] + rows + [separator]
        return '\n'.join(table)

    def validate_ticker(self, ticker):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM Fundamentals WHERE Ticker = ?", (ticker,))
        return cursor.fetchone() is not None

    def initialize_vector_store(self):
        # Populate vector store with recent articles
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT title, summary 
            FROM Articles 
            WHERE time_published >= datetime('now', '-30 days')
        """)
        articles = cursor.fetchall()
        
        texts = [f"Title: {title}\nSummary: {summary}" for title, summary in articles]
        global vector_store
        vector_store = FAISS.from_texts(texts, embedding_model)

# --- MAIN LOOP ---
if __name__ == "__main__":
    agent = RAGAgent()
    agent.initialize_vector_store()  # Initialize vector store with recent articles
    print("🚀 RAG Agent initialized and ready!")
    
    while True:
        try:
            user_input = input("\n>> Enter your query (or type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            response = agent.generate_response(user_input)
            print("\nResponse:")
            print(response)
        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
