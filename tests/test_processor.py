import unittest
import os
import shutil
import zipfile
import pandas as pd
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_ingestion.processor import DataProcessor

class TestDataProcessor(unittest.TestCase):

    def setUp(self):
        """Set up a test environment before each test."""
        self.download_dir = "test_download_dir"
        self.extract_dir = "test_extract_dir"
        self.processor = DataProcessor(self.download_dir, self.extract_dir, 'latin-1', -999)
        for dir_path in [self.download_dir, self.extract_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            os.makedirs(dir_path)

    def tearDown(self):
        """Clean up the test environment after each test."""
        for dir_path in [self.download_dir, self.extract_dir]:
            shutil.rmtree(dir_path)

    def test_process_file(self):
        """Test that zip files are correctly unzipped and filtered."""
        zip_path = os.path.join(self.download_dir, "test_archive.zip")
        product_filename = "produkt_klima_tag_123.txt"
        metadata_filename = "Metadaten_klima_123.txt"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr(product_filename, "header line 1\nSTATIONS_ID;MESS_DATUM; QN_3; FX; FM; QN_4; RSK; RSKF; SDK; SHK_TAG; NM; VPM; PM; TMK; UPM; TXK; TNK; TGK; eor\n   123;20230101;    1; 10.0;  5.0;    3; 0.5;     1;   8.0;     0; 7.0;10.0;1010.0; 5.0;70.0; 8.0; 2.0; 1.0;eor\n")
            zipf.writestr(metadata_filename, "dummy metadata")

        # Run the method with the specific pattern to extract
        csv_file_path = self.processor.process_file(zip_path, 'produkt_', 'STATIONS_ID', ';')

        self.assertIsNotNone(csv_file_path)
        self.assertTrue(os.path.exists(csv_file_path))
        self.assertFalse(os.path.exists(os.path.join(self.extract_dir, product_filename)))
        
        df = pd.read_csv(csv_file_path, sep=';')
        self.assertEqual(df.shape[0], 1)
        self.assertIn('TMK', df.columns)
        self.assertEqual(df.iloc[0]['TMK'], 5.0)


if __name__ == '__main__':
    unittest.main()