import requests
import re
import os

class DWDDownloader:
    """Handles downloading data files from the DWD server."""
    def __init__(self, download_dir="data"):
        self.dwd_url = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"
        self.download_dir = download_dir

    def get_file_urls(self):
        """Gets all the file urls from the DWD Open Data Server."""
        print("Fetching file list from DWD server...")
        response = requests.get(self.dwd_url)
        response.raise_for_status()

        pattern = r'href="(tageswerte_KL_.*?\.zip)"'
        file_names = re.findall(pattern, response.text)
        file_urls = [self.dwd_url + file_name for file_name in file_names]
        print(f"Found {len(file_urls)} files.")
        return file_urls

    def download_files(self, urls, limit=None):
        """Downloads files from a list of URLs into a specified directory."""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        files_to_download = urls[:limit] if limit else urls
        if limit:
            print(f"Limiting download to {limit} files.")

        for url in files_to_download:
            file_name = url.split('/')[-1]
            local_path = os.path.join(self.download_dir, file_name)
            
            if os.path.exists(local_path):
                print(f"File {file_name} already exists. Skipping.")
                continue

            print(f"Downloading {url}...")
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Successfully downloaded {file_name}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {url}. Error: {e}")

    def run(self, limit=None):
        """Runs the complete download process."""
        file_urls = self.get_file_urls()
        self.download_files(file_urls, limit=limit)
        print("\nFile download process finished.")
