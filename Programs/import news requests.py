import requests
from datetime import datetime, timedelta
import pandas as pd
import time

# Alpha Vantage API key
API_KEY = 'HI5ADT0RWWANGUID'

# Base URL for the Alpha Vantage news API
BASE_URL = 'https://www.alphavantage.co/query'

# Function to fetch general market news with pagination
def fetch_news(start_date, end_date, limit=1000):
    """
    Fetches general market news articles between specified dates with pagination.

    Parameters:
        start_date (str): Start date in YYYYMMDDTHHMM format.
        end_date (str): End date in YYYYMMDDTHHMM format.
        limit (int): The maximum number of articles to fetch per request.

    Returns:
        pd.DataFrame: A DataFrame containing the news articles.
    """
    all_news = []
    current_start = start_date

    while True:
        # Define parameters for the API request
        params = {
            'function': 'NEWS_SENTIMENT',  # API function for news sentiment
            'apikey': API_KEY,             # API key
            'time_from': current_start,    # Current start date
            'time_to': end_date,           # End date
            'limit': limit,                # Limit number of results
            'sort': 'LATEST'               # Sort articles by latest
        }

        # Make the API request
        response = requests.get(BASE_URL, params=params)

        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()

            # Extract relevant news articles
            if 'feed' in data:
                news_items = data['feed']
                all_news.extend(news_items)

                # Check if we received fewer articles than the limit, indicating the last batch
                if len(news_items) < limit:
                    break

                # Update current_start to the time of the last article to fetch the next batch
                last_article_time = news_items[-1]['time_published']
                current_start = last_article_time

                # Throttle API requests to avoid exceeding rate limits
                print(f"Fetched {len(news_items)} articles. Waiting 12 seconds...")
                time.sleep(12)  # 5 requests per minute = 12 seconds between requests

            else:
                print("No more news data found.")
                break
        else:
            print(f"Error fetching data: {response.status_code}")
            break

    # Convert the accumulated news data into a pandas DataFrame
    return pd.DataFrame(all_news)

# Date range from October 1, 2024 to December 1, 2024
start_date = datetime(2024, 10, 1)
end_date = datetime(2024, 12, 1)

# Fetch news day by day
current_date = start_date
monthly_data = {}

while current_date < end_date:
    # Define start and end dates for the current day
    day_start = current_date
    day_end = current_date + timedelta(days=1)
    if day_end > end_date:
        day_end = end_date  # Cap at the final date

    # Format dates in YYYYMMDDTHHMM format
    start_date_str = day_start.strftime('%Y%m%dT%H%M')
    end_date_str = day_end.strftime('%Y%m%dT%H%M')

    print(f"Fetching news from {start_date_str} to {end_date_str}")

    # Fetch general news data with pagination
    news_df = fetch_news(start_date_str, end_date_str)

    # Append data to the corresponding month
    month_key = day_start.strftime('%Y_%m')
    if month_key not in monthly_data:
        monthly_data[month_key] = pd.DataFrame()

    if not news_df.empty:
        monthly_data[month_key] = pd.concat([monthly_data[month_key], news_df], ignore_index=True)

    # Move to the next day
    current_date = day_end

# Save the data to monthly CSV files
for month_key, df in monthly_data.items():
    if not df.empty:
        output_path = f"C:\\Users\\Jrans\\Desktop\\AI Project\\Hdata\\News\\news_{month_key}.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved news to {output_path}")