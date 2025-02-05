# Agent_Project25

## Large Files Handling

Some data files in this project are split into smaller chunks for GitHub compatibility. The following files are split:

- `Data/PreProcessed/Agent_Project25.db`
- `Data/PreProcessed/combined_insider_transactions.csv`
- `Data/PreProcessed/executive_ticker_relationships.csv`

### Working with Split Files

Two Python scripts are provided to handle the split files:

1. `split_large_files.py`: Splits large files into manageable chunks
2. `recombine_files.py`: Recombines the chunks back into their original files

#### Requirements

Install required Python packages:
```bash
pip install -r requirements.txt
```

#### Recombining Files

After cloning the repository, run:
```bash
python recombine_files.py
```

This will:
- Recombine the CSV chunks into their original files
- Reconstruct the SQLite database from its table chunks

The recombined files will be placed in their original locations in the `Data/PreProcessed/` directory.

## Project Structure

- `Data/`: Contains all data files
  - `Fundamentals/`: Fundamental data files
  - `InsiderTran/`: Insider transaction data
  - `News/`: News data files
  - `PreProcessed/`: Preprocessed data files
  - `Price/`: Price data files
  - `Unusual_Options/`: Options data
- `Programs/`: Data import and processing scripts
- `src/`: Source code files
  - `database.py`: Database operations
  - `rag_agent.py`: RAG agent implementation
