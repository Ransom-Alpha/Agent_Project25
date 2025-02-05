# Agent_Project25

A financial analysis application that combines RAG (Retrieval Augmented Generation) and technical analysis capabilities with a user-friendly GUI interface.

## Initial Setup After Cloning

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Agent_Project25.git
cd Agent_Project25
```

2. Create and activate virtual environment:
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize data directories:
The repository includes empty data directories that will be populated during processing:
- `Data/Fundamentals/`: Company fundamental data
- `Data/InsiderTran/`: Insider transaction data
- `Data/News/`: Financial news data
- `Data/Price/`: Stock price data
- `Data/Unusual_Options/`: Options data
- `Data/PreProcessed/`: Will store processed data files

5. Run data processing and database creation:
```bash
python 1_DBcreationAgent.py
```

## Project Structure

- `Data/`: Contains all data files
  - `Fundamentals/`: Fundamental data files
  - `InsiderTran/`: Insider transaction data
  - `News/`: News data files
  - `PreProcessed/`: Preprocessed data files
  - `Price/`: Price data files
  - `Unusual_Options/`: Options data
- `src/`: Source code files
  - `database.py`: Database operations
  - `gui.py`: Main GUI implementation
  - `Agents/`: Agent implementations
    - `rag_agent.py`: RAG agent for natural language queries
    - `technical_analysis_agent.py`: Technical analysis capabilities
- `Supplement_Files/`: Data processing and database scripts
  - `PreProcess/`: Data preprocessing scripts
  - `SQLiteDB1.py`: Database creation script
  - `ImportDataDB2.py`: Data import script

## Data Processing and Database Setup

The `1_DBcreationAgent.py` script automates the entire database setup process:
- Runs all preprocessing scripts in `Supplement_Files/PreProcess/`
- Creates the SQLite database using `SQLiteDB1.py`
- Imports processed data using `ImportDataDB2.py`

The process handles:
- Processing raw financial data
- Creating necessary database tables
- Importing preprocessed data into the database
- Setting up relationships between different data types

Monitor the console output for progress indicators:
- 🔄 indicates preprocessing in progress
- 🚀 shows database creation
- 📥 indicates data import
- ✅ confirms successful completion
- ❌ warns of any errors

## Running the Application

1. Ensure your virtual environment is activated
2. Run the GUI:
```bash
python -m src.launch_gui
```

## Features

- Interactive GUI with split-pane view
- RAG Agent for natural language queries about:
  - Company news
  - Fundamental data
  - Insider transactions
- Technical Analysis Agent for:
  - Price analysis
  - Chart generation
  - Technical indicators

## Data Sources

The application processes and analyzes data from multiple sources:
- Stock price data
- Company fundamentals
- Insider transactions
- News articles
- Options data

## Requirements

See `requirements.txt` for a complete list of dependencies. Key requirements include:
- Python 3.8+
- tkinter for GUI
- matplotlib for charts
- langchain and chromadb for RAG capabilities
- yfinance for market data

## Git Repository Structure

The repository is structured to:
- Track all source code and configuration files
- Maintain empty data directory structure
- Exclude:
  - Virtual environment (venv/)
  - Generated databases and large data files
  - Python cache files
  - IDE-specific files
  - Log files
  - Environment variables (.env)

This ensures that users can clone the repository and generate their own data files while keeping the repository size manageable.
