import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
import sys

# Add the project root to the Python path to allow importing 'wetter'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_ingestion.downloader import Downloader

class TestDownloader(unittest.TestCase):

    def setUp(self):
        """Set up a test environment before each test."""
        self.test_dir = "test_data"
        self.test_url = "https://example.com/data/"
        self.downloader = Downloader(url=self.test_url, download_dir=self.test_dir)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

    def tearDown(self):
        """Clean up the test environment after each test."""
        shutil.rmtree(self.test_dir)

    @patch('requests.get')
    def test_get_file_urls(self, mock_get):
        """Test that file URLs are correctly extracted from mock HTML."""
        mock_html = '''
        <html><body>
        <a href="file1.zip">file1.zip</a>
        <a href="file2.zip">file2.zip</a>
        <a href="other_file.txt">some other file</a>
        </body></html>
        '''
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = mock_html
        mock_get.return_value = mock_response

        # The pattern to match in the mock HTML
        test_pattern = r'href="(file.*?\.zip)"'
        urls = self.downloader.get_file_urls(pattern=test_pattern)

        self.assertEqual(len(urls), 2)
        self.assertIn(self.test_url + "file1.zip", urls)
        self.assertIn(self.test_url + "file2.zip", urls)

    @patch('requests.get')
    def test_download_files(self, mock_get):
        """Test that files are downloaded correctly."""
        mock_file_content = b'dummy zip content'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [mock_file_content]
        mock_get.return_value = mock_response

        test_urls = [self.test_url + "dummy_file.zip"]
        
        for url in test_urls:
            self.downloader.download_file(url)

        expected_file_path = os.path.join(self.test_dir, "dummy_file.zip")
        self.assertTrue(os.path.exists(expected_file_path))
        with open(expected_file_path, 'rb') as f:
            content = f.read()
        self.assertEqual(content, mock_file_content)

if __name__ == '__main__':
    unittest.main()
