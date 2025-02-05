import os
import subprocess
import sys

class DatabaseAgent:
    def __init__(self):
        self.preprocess_folder = os.path.join('Supplement_Files', 'PreProcess')
        self.scripts_folder = 'Supplement_Files'
        self.sqlite_script = os.path.join(self.scripts_folder, 'SQLiteDB1.py')
        self.import_script = os.path.join(self.scripts_folder, 'ImportDataDB2.py')

    def preprocess_data(self):
        print("🔄 Starting data preprocessing...")
        
        # Process each file in the PreProcess folder
        for file_name in os.listdir(self.preprocess_folder):
            file_path = os.path.join(self.preprocess_folder, file_name)

            if file_name.endswith('.py'):
                try:
                    print(f"⚙️ Running preprocessing script: {file_name}")
                    subprocess.run([sys.executable, file_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error processing {file_name}: {e}")

        print("✅ Data preprocessing completed.")

    def create_database(self):
        print("🚀 Creating SQLite Database...")
        try:
            subprocess.run([sys.executable, self.sqlite_script], check=True)
            print("✅ SQLite Database created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating SQLite Database: {e}")

    def import_data(self):
        print("📥 Importing data into the database...")
        try:
            subprocess.run([sys.executable, self.import_script], check=True)
            print("✅ Data imported successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error importing data: {e}")

    def run(self):
        self.preprocess_data()
        self.create_database()
        self.import_data()

if __name__ == "__main__":
    agent = DatabaseAgent()
    agent.run()
