import pandas as pd
import matplotlib.pyplot as plt
from .rag_agent import RAGAgent

class TechnicalAnalysisAgent:
    def __init__(self):
        self.rag_agent = RAGAgent()

    def fetch_price_data(self, ticker, timespan):
        # Format query to match RAG agent expectations - ALL CAPS ticker without parentheses
        ticker = ticker.strip('()').upper()
        # Request more data to properly calculate moving averages
        query_timespan = max(timespan, 250)  # At least 250 days for 200MA
        query = f"Grab {ticker} price data for the last {query_timespan} days"
        raw_data = self.rag_agent.fetch_price_data(query)

        if isinstance(raw_data, str):
            # Split the raw string into lines and find the data rows
            lines = raw_data.split('\n')
            data_rows = []
            header_found = False
            
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Skip header row and separator
                if 'Date' in line or '-+-' in line:
                    header_found = True
                    continue
                    
                # Only process data rows after header
                if header_found and '|' in line:
                    # Parse the row data
                    cols = [col.strip() for col in line.split('|')[1:-1]]  # Split by | and remove first/last empty elements
                    if len(cols) == 6:  # Ensure we have all columns
                        data_rows.append(cols)

            if not data_rows:
                print("No valid data rows found")
                return pd.DataFrame()

            # Create DataFrame from parsed rows
            df = pd.DataFrame(data_rows, columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
            # Convert types
            df['Date'] = pd.to_datetime(df['Date'])
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
            
            # Data comes in reverse chronological order (newest first)
            # Sort by date ascending (oldest first) for technical analysis
            df = df.sort_values('Date', ascending=True)
            
            # Reset index after sorting to ensure proper calculations
            df = df.reset_index(drop=True)
            
            # Verify we have the expected number of days
            if len(df) < timespan:
                print(f"Warning: Only got {len(df)} days of data, requested {timespan}")
            
            return df
        
        return pd.DataFrame()  # Return empty DataFrame if raw_data is not a string

    def calculate_indicators(self, df):
        if len(df) < 200:
            print("Warning: Insufficient data for reliable 200-day moving average")
            return df
            
        # Moving Averages - require full window of data
        df['50_SMA'] = df['Close'].rolling(window=50, min_periods=50).mean()
        df['200_SMA'] = df['Close'].rolling(window=200, min_periods=200).mean()
        df['10_EMA'] = df['Close'].ewm(span=10, adjust=False, min_periods=10).mean()
        df['20_EMA'] = df['Close'].ewm(span=20, adjust=False, min_periods=20).mean()

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
        # Only calculate signals where we have both moving averages
        valid_ma_data = df.dropna(subset=['50_SMA', '200_SMA'])
        
        if len(valid_ma_data) < 2:  # Need at least 2 points to detect crossover
            df['Golden_Cross'] = False
            df['Death_Cross'] = False
        else:
            # Moving Average Crossovers - only where we have both MAs
            df['Golden_Cross'] = (df['50_SMA'] > df['200_SMA']) & (df['50_SMA'].shift(1) <= df['200_SMA'].shift(1))
            df['Death_Cross'] = (df['50_SMA'] < df['200_SMA']) & (df['50_SMA'].shift(1) >= df['200_SMA'].shift(1))
        
        # RSI Signals - only where RSI is not null
        valid_rsi = df.dropna(subset=['RSI'])
        if len(valid_rsi) < 2:  # Need at least 2 points to detect crossover
            df['RSI_Buy_Signal'] = False
            df['RSI_Sell_Signal'] = False
        else:
            df['RSI_Buy_Signal'] = (df['RSI'] < 20) & (df['RSI'].shift(1) >= 20)
            df['RSI_Sell_Signal'] = (df['RSI'] > 80) & (df['RSI'].shift(1) <= 80)

        return df

    def create_analysis_charts(self, df, ticker):
        """Create and return matplotlib figure with analysis charts"""
        fig = plt.figure(figsize=(14, 8))

        # Price Chart with Moving Averages
        ax1 = plt.subplot(3, 1, 1)
        ax1.plot(df['Date'], df['Close'], label='Close Price', color='blue')
        ax1.plot(df['Date'], df['50_SMA'], label='50 SMA', color='orange')
        ax1.plot(df['Date'], df['200_SMA'], label='200 SMA', color='red')
        ax1.scatter(df[df['Golden_Cross']]['Date'], df[df['Golden_Cross']]['Close'], 
                   label='Golden Cross', marker='^', color='green')
        ax1.scatter(df[df['Death_Cross']]['Date'], df[df['Death_Cross']]['Close'], 
                   label='Death Cross', marker='v', color='red')
        ax1.set_title(f'{ticker} Price with Moving Averages and Signals')
        ax1.legend()

        # RSI Chart
        ax2 = plt.subplot(3, 1, 2)
        ax2.plot(df['Date'], df['RSI'], label='RSI', color='purple')
        ax2.scatter(df[df['RSI_Buy_Signal']]['Date'], df[df['RSI_Buy_Signal']]['RSI'], 
                   label='RSI Buy Signal', marker='^', color='green')
        ax2.scatter(df[df['RSI_Sell_Signal']]['Date'], df[df['RSI_Sell_Signal']]['RSI'], 
                   label='RSI Sell Signal', marker='v', color='red')
        ax2.axhline(80, color='red', linestyle='--')
        ax2.axhline(20, color='green', linestyle='--')
        ax2.set_title('RSI')
        ax2.legend()

        # ADX Chart
        ax3 = plt.subplot(3, 1, 3)
        ax3.plot(df['Date'], df['ADX'], label='ADX', color='brown')
        ax3.set_title('ADX')
        ax3.legend()

        plt.tight_layout()
        return fig

    def analyze_ticker(self, query):
        """Analyze ticker based on query and return results"""
        # Extract ticker and timespan from query
        import re
        ticker_match = re.search(r'\(([^)]+)\)', query)
        days_match = re.search(r'(\d+)\s*days', query)
        
        if not ticker_match:
            return "Please specify a ticker in parentheses, e.g., (AAPL)", None
            
        ticker = ticker_match.group(1)
        display_timespan = int(days_match.group(1)) if days_match else 30

        # Fetch extra historical data for proper MA calculations
        df = self.fetch_price_data(ticker, display_timespan + 200)  # Get 200 extra days
        if df.empty:
            return "No data available for analysis.", None

        # Calculate indicators on full dataset
        df = self.calculate_indicators(df)
        df = self.identify_signals(df)
        
        # Calculate the display window
        if len(df) > display_timespan:
            # Get the most recent display_timespan days
            display_df = df.tail(display_timespan).copy()
        else:
            # Use all available data if we have less than requested
            display_df = df.copy()
        
        # Reset index for clean plotting
        display_df = display_df.reset_index(drop=True)
        
        # Generate analysis text using the most recent data point in the display timespan
        last_row = display_df.iloc[-1]
        analysis_text = f"Technical Analysis Summary for {ticker}:\n\n"
        analysis_text += f"Current Price: ${last_row['Close']:.2f}\n"
        analysis_text += f"RSI: {last_row['RSI']:.2f}\n"
        analysis_text += f"ADX: {last_row['ADX']:.2f}\n\n"
        
        # Check for signals within the display timespan
        if display_df['Golden_Cross'].any():
            analysis_text += "Signal: Golden Cross detected! Bullish signal.\n"
        elif display_df['Death_Cross'].any():
            analysis_text += "Signal: Death Cross detected! Bearish signal.\n"
        
        if last_row['RSI'] > 70:
            analysis_text += "RSI indicates overbought conditions.\n"
        elif last_row['RSI'] < 30:
            analysis_text += "RSI indicates oversold conditions.\n"
            
        # Create charts using the trimmed display dataset
        fig = self.create_analysis_charts(display_df, ticker)
        
        return analysis_text, fig

if __name__ == "__main__":
    agent = TechnicalAnalysisAgent()
    while True:
        user_input = input("Enter your technical analysis query (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        if '(' in user_input and ')' in user_input:
            analysis_text, fig = agent.analyze_ticker(user_input)
            print(analysis_text)
            if fig:
                plt.show()
        else:
            print("Please specify a ticker in parentheses, e.g., (AAPL).")
