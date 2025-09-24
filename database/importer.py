import os
from database.database import Database

class CsvImporter:
    def __init__(self, db: Database):
        self.db = db
        self.unzipped_dir = os.path.join('data', 'unzipped')

    def run(self):
        """
        Uses an existing database connection to find all CSV files in the
        'data/unzipped' directory and insert them.
        """
        print("--- Running CSV Importer ---")
        if not self.db.conn:
            print("Database connection is not available. Aborting import.")
            return

        try:
            print(f"Searching for CSV files in '{self.unzipped_dir}'...")
            if not os.path.isdir(self.unzipped_dir):
                print(f"Error: Directory not found at '{self.unzipped_dir}'.")
                return

            csv_files = [f for f in os.listdir(self.unzipped_dir) if f.lower().endswith('.csv')]

            if not csv_files:
                print("No CSV files found to import.")
                return

            print(f"Found {len(csv_files)} CSV file(s): {', '.join(csv_files)}")
            for filename in csv_files:
                full_path = os.path.join(self.unzipped_dir, filename)
                print(f"Importing '{filename}'...")
                self.db.insert_csv(full_path)
            print("CSV import process finished.")

        except Exception as e:
            print(f"An unexpected error occurred during CSV import: {e}")
