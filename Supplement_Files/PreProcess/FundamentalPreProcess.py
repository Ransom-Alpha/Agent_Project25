import pandas as pd
import os

# Folder containing the fundamental data file
fundamentals_folder = 'Data/Fundamentals/'  # Update this path if different
preprocessed_folder = 'Data/PreProcessed/'  # Folder to save preprocessed files

# Ensure the preprocessed folder exists
os.makedirs(preprocessed_folder, exist_ok=True)

# Process all CSV files in the folder
for filename in os.listdir(fundamentals_folder):
    if filename.endswith('.csv'):
        file_path = os.path.join(fundamentals_folder, filename)

        # Extract date from filename
        file_date = filename.replace('.csv', '')
        file_date = pd.to_datetime(file_date, errors='coerce')

        # Load the fundamental data
        df = pd.read_csv(file_path)

        # Remove the pegRatio column
        if 'pegRatio' in df.columns:
            df.drop(columns=['pegRatio'], inplace=True)

        # Fill missing values
        df['sector'].fillna('NULL', inplace=True)
        df['recommendationKey'].fillna('NULL', inplace=True)

        # Add date column
        df['date'] = file_date

        # Save the preprocessed file
        preprocessed_filename = f'preprocessed_{filename}'
        preprocessed_path = os.path.join(preprocessed_folder, preprocessed_filename)
        df.to_csv(preprocessed_path, index=False)

        print(f'✅ Preprocessed and saved: {preprocessed_filename}')
