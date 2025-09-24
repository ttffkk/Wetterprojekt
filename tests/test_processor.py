import unittest
import os
import shutil
import zipfile
import pandas as pd
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from wetter.processor import DataProcessor

class TestDataProcessor(unittest.TestCase):

    def setUp(self):
        """Set up a test environment before each test."""
        self.download_dir = "test_download_dir"
        self.extract_dir = "test_extract_dir"
        for dir_path in [self.download_dir, self.extract_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
            os.makedirs(dir_path)
        self.processor = DataProcessor(download_dir=self.download_dir, extract_dir=self.extract_dir)

    def tearDown(self):
        """Clean up the test environment after each test."""
        for dir_path in [self.download_dir, self.extract_dir]:
            shutil.rmtree(dir_path)

    def test_unzip_and_filter_files(self):
        """Test that zip files are correctly unzipped and filtered."""
        zip_path = os.path.join(self.download_dir, "test_archive.zip")
        product_filename = "produkt_klima_tag_123.txt"
        metadata_filename = "Metadaten_klima_123.txt"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.writestr(product_filename, "dummy data")
            zipf.writestr(metadata_filename, "dummy metadata")

        # Run the method with the specific pattern to extract
        self.processor.unzip_and_filter_files(file_pattern_to_extract='produkt_')

        self.assertTrue(os.path.exists(os.path.join(self.extract_dir, product_filename)))
        self.assertFalse(os.path.exists(os.path.join(self.extract_dir, metadata_filename)))
        self.assertFalse(os.path.exists(zip_path))

    def test_parse_data_files(self):
        """Test the parsing of data files."""
        file_content = (
            "header line 1\n"
            "STATIONS_ID;MESS_DATUM; QN_3; FX; FM; QN_4; RSK; RSKF; SDK; SHK_TAG; NM; VPM; PM; TMK; UPM; TXK; TNK; TGK; eor\n"
            "   123;20230101;    1; 10.0;  5.0;    3; 0.5;     1;   8.0;     0; 7.0;10.0;1010.0; 5.0;70.0; 8.0; 2.0; 1.0;eor\n"
            "   123;20230102;    1;-999; -999;    3; 2.0;     0;   -999;     0; 6.0;11.0;1012.0; 6.0;75.0; 9.0; 3.0;-999;eor\n"
        )
        data_file_path = os.path.join(self.extract_dir, "produkt_test.txt")
        with open(data_file_path, "w", encoding='latin-1') as f:
            f.write(file_content)

        # Run the method with parsing parameters
        df = self.processor.parse_data_files(
            file_glob="produkt_*.txt",
            header_keyword='STATIONS_ID',
            delimiter=';'
        )

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 2)
        self.assertIn('TMK', df.columns)
        self.assertEqual(df.iloc[0]['TMK'], 5.0)
        self.assertTrue(pd.isna(df.iloc[1]['FX']))
        self.assertTrue(pd.isna(df.iloc[1]['SDK']))
        self.assertTrue(pd.isna(df.iloc[1]['TGK']))

if __name__ == '__main__':
    unittest.main()
