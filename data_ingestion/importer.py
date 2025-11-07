import os
from .database import Database

class CsvImporter:
    def __init__(self, db: Database):
        self.db = db

    def import_file(self, file_path, delimiter):
        """
        Uses an existing database connection to insert a single CSV file.
        """
        print("--- Running CSV Importer ---")
        if not self.db.conn:
            print("Database connection is not available. Aborting import.")
            return

        try:
            print(f"Importing '{os.path.basename(file_path)}'...")
            self.db.insert_csv(file_path, delimiter)
            print("CSV import process finished.")

        except Exception as e:
            print(f"An unexpected error occurred during CSV import: {e}")


class ParameterImporter:
    def __init__(self, db: Database):
        self.db = db

    def import_parameters(self, file_path):
        print("--- Running Parameter Importer ---")
        if not self.db.conn:
            print("Database connection is not available. Aborting import.")
            return

        try:
            print(f"Importing '{os.path.basename(file_path)}'...")
            self.db.insert_parameters(file_path)
            print("Parameter import process finished.")

        except Exception as e:
            print(f"An unexpected error occurred during parameter import: {e}")
