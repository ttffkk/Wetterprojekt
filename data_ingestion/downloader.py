import requests
import re
import os

class Downloader:
    """Handles downloading data files from a given URL."""
    def __init__(self, url, download_dir):
        self.url = url
        self.download_dir = download_dir

    def get_file_urls(self, pattern):
        """Gets all the file urls from the server that match the pattern."""
        print(f"Fetching file list from {self.url}...")
        response = requests.get(self.url)
        response.raise_for_status()

        file_names = re.findall(pattern, response.text)
        file_urls = [self.url + file_name for file_name in file_names]
        print(f"Found {len(file_urls)} files matching the pattern.")
        return file_urls

    def download_file(self, url):
        """Downloads a single file from a URL into a specified directory."""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        file_name = url.split('/')[-1]
        local_path = os.path.join(self.download_dir, file_name)

        if os.path.exists(local_path):
            print(f"File {file_name} already exists. Skipping.")
            return local_path

        print(f"Downloading {url}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Successfully downloaded {file_name}")
            return local_path
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}. Error: {e}")
            return None
            
    def download_station_file(self, station_url):
        """Downloads the station description file."""
        print("Downloading station description file...")
        return self.download_file(station_url)
