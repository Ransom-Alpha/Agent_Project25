import pandas as pd
import ast
import os
from datetime import datetime

# Folder containing news files
news_folder = 'Data/News/'

# Lists to store processed data
articles_data = []
ticker_relationships = []
topic_relationships = []

# Function to parse JSON-like fields safely
def parse_json_field(field):
    try:
        return ast.literal_eval(field)
    except (ValueError, SyntaxError):
        return []

# Function to format date
def format_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y%m%dT%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

# Process all news files
for filename in os.listdir(news_folder):
    if filename.endswith('.csv') and filename.startswith('news_'):
        file_path = os.path.join(news_folder, filename)
        news_df = pd.read_csv(file_path)
        
        # Process each article
        for index, row in news_df.iterrows():
            article_id = f"{filename}_{index}"  # Unique article ID
            date_published = format_date(row['time_published'])
            
            # Add article metadata
            articles_data.append({
                'article_id': article_id,
                'title': row.get('title'),
                'summary': row.get('summary'),
                'time_published': date_published,
                'source': row.get('source'),
                'overall_sentiment_score': row.get('overall_sentiment_score'),
                'overall_sentiment_label': row.get('overall_sentiment_label')
            })
            
            # Extract ticker relationships
            ticker_sentiments = parse_json_field(row.get('ticker_sentiment', '[]'))
            for sentiment in ticker_sentiments:
                ticker_relationships.append({
                    'article_id': article_id,
                    'ticker': sentiment.get('ticker'),
                    'sentiment_score': sentiment.get('sentiment_score'),
                    'sentiment_label': sentiment.get('sentiment_label'),
                    'relevance_score': sentiment.get('relevance_score'),
                    'date': date_published.split(' ')[0]  # For time-series queries
                })
            
            # Extract topic relationships
            topics = parse_json_field(row.get('topics', '[]'))
            for topic in topics:
                topic_relationships.append({
                    'article_id': article_id,
                    'topic': topic.get('topic'),
                    'relevance_score': topic.get('relevance_score'),
                    'date': date_published.split(' ')[0]
                })

# Convert to DataFrames
articles_df = pd.DataFrame(articles_data)
ticker_relationships_df = pd.DataFrame(ticker_relationships)
topic_relationships_df = pd.DataFrame(topic_relationships)

# Save as CSV for Neo4j Import
articles_df.to_csv('data/News/articles.csv', index=False)
ticker_relationships_df.to_csv('data/News/article_ticker_relationships.csv', index=False)
topic_relationships_df.to_csv('data/News/article_topic_relationships.csv', index=False)

print("✅ Preprocessing complete! Files saved for Neo4j import.")
