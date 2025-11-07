
import unittest
import os
import sqlite3
from data_ingestion.database import Database
from data_ingestion.importer import CsvImporter

class TestCsvImporter(unittest.TestCase):

    def setUp(self):
        self.db_path = os.path.abspath('test_importer.db')
        self.csv_path = os.path.abspath('test_data.csv')
        self.sql_path = os.path.abspath('Create_table.sql')

        # Create a dummy CSV file
        with open(self.csv_path, 'w') as f:
            f.write('STATIONS_ID;MESS_DATUM;QN_3;FX;FM;QN_4;RSK;RSKF;SDK;SHK_TAG;NM;VPM;PM;TMK;UPM;TXK;TNK;TGK;eor\n')
            f.write('1;20230101;1;1;1;1;1;1;1;1;1;1;1;12.3;1;1;1;1;eor\n')

        # Create a database and tables
        self.db = Database(self.db_path, 'NA', 'utf-8')
        self.db.create_connection()
        self.db.create_tables(self.sql_path)

    def tearDown(self):
        self.db.close_connection()
        os.remove(self.db_path)
        os.remove(self.csv_path)

    def test_import_file(self):
        importer = CsvImporter(self.db)
        importer.import_file(self.csv_path, ';')

        # Check if the data was inserted
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Measurement WHERE Station_ID = 1 AND MESS_DATUM = 20230101")
        data = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(data)
        self.assertEqual(data[14], 12.3)

if __name__ == '__main__':
    unittest.main()
