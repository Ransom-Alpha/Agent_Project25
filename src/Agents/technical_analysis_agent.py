import pandas as pd
import matplotlib.pyplot as plt
from src.Agents.rag_agent import RAGAgent

class TechnicalAnalysisAgent:
    def __init__(self):
        self.rag_agent = RAGAgent()

    def fetch_price_data(self, ticker, timespan):
        query = f"Grab ({ticker}) price data for the last {timespan} days"
        raw_data = self.rag_agent.fetch_price_data(query)

        if isinstance(raw_data, str):  # Check if an error message was returned
            print(raw_data)
            return pd.DataFrame()

        df = pd.DataFrame(raw_data, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker'])
        df['Date'] = pd.to_datetime(df['Date'])
        return df

    def calculate_indicators(self, df):
        # Moving Averages
        df['50_SMA'] = df['Close'].rolling(window=50, min_periods=1).mean()
        df['200_SMA'] = df['Close'].rolling(window=200, min_periods=1).mean()
        df['10_EMA'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['20_EMA'] = df['Close'].ewm(span=20, adjust=False).mean()

        # RSI Calculation
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # ADX Calculation
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))

        tr = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        atr = tr.rolling(window=14).mean()

        df['+DM'] = df['High'].diff().apply(lambda x: x if x > 0 else 0)
        df['-DM'] = df['Low'].diff().apply(lambda x: -x if x < 0 else 0)

        df['+DI'] = 100 * (df['+DM'].rolling(window=14).mean() / atr)
        df['-DI'] = 100 * (df['-DM'].rolling(window=14).mean() / atr)

        df['DX'] = (abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])) * 100
        df['ADX'] = df['DX'].rolling(window=14).mean()

        return df

    def identify_signals(self, df):
        # RSI Signals
        df['RSI_Buy_Signal'] = (df['RSI'] < 20) & (df['RSI'].shift(1) >= 20)
        df['RSI_Sell_Signal'] = (df['RSI'] > 80) & (df['RSI'].shift(1) <= 80)

        # Moving Average Crossovers
        df['Golden_Cross'] = (df['50_SMA'] > df['200_SMA']) & (df['50_SMA'].shift(1) <= df['200_SMA'].shift(1))
        df['Death_Cross'] = (df['50_SMA'] < df['200_SMA']) & (df['50_SMA'].shift(1) >= df['200_SMA'].shift(1))

        return df

    def plot_charts(self, df, ticker):
        plt.figure(figsize=(14, 8))

        # Price Chart with Moving Averages
        plt.subplot(3, 1, 1)
        plt.plot(df['Date'], df['Close'], label='Close Price', color='blue')
        plt.plot(df['Date'], df['50_SMA'], label='50 SMA', color='orange')
        plt.plot(df['Date'], df['200_SMA'], label='200 SMA', color='red')
        plt.scatter(df[df['Golden_Cross']]['Date'], df[df['Golden_Cross']]['Close'], label='Golden Cross', marker='^', color='green')
        plt.scatter(df[df['Death_Cross']]['Date'], df[df['Death_Cross']]['Close'], label='Death Cross', marker='v', color='red')
        plt.title(f'{ticker} Price with Moving Averages and Signals')
        plt.legend()

        # RSI Chart
        plt.subplot(3, 1, 2)
        plt.plot(df['Date'], df['RSI'], label='RSI', color='purple')
        plt.scatter(df[df['RSI_Buy_Signal']]['Date'], df[df['RSI_Buy_Signal']]['RSI'], label='RSI Buy Signal', marker='^', color='green')
        plt.scatter(df[df['RSI_Sell_Signal']]['Date'], df[df['RSI_Sell_Signal']]['RSI'], label='RSI Sell Signal', marker='v', color='red')
        plt.axhline(80, color='red', linestyle='--')
        plt.axhline(20, color='green', linestyle='--')
        plt.title('RSI')
        plt.legend()

        # ADX Chart
        plt.subplot(3, 1, 3)
        plt.plot(df['Date'], df['ADX'], label='ADX', color='brown')
        plt.title('ADX')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def analyze_ticker(self, ticker, timespan=30):
        df = self.fetch_price_data(ticker, timespan)
        if df.empty:
            print("No data available for analysis.")
            return

        df = self.calculate_indicators(df)
        df = self.identify_signals(df)
        print(df.tail())  # Display the last few rows with indicators and signals
        self.plot_charts(df, ticker)

if __name__ == "__main__":
    agent = TechnicalAnalysisAgent()
    while True:
        user_input = input("Enter your technical analysis query (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        import re
        ticker_match = re.search(r'\(([^)]+)\)', user_input)
        days_match = re.search(r'(\d+)\s*days', user_input)

        ticker = ticker_match.group(1) if ticker_match else None
        timespan = int(days_match.group(1)) if days_match else 30  # Default to 30 days

        if ticker:
            agent.analyze_ticker(ticker, timespan)
        else:
            print("Please specify a ticker in parentheses, e.g., (AAPL).")
