import requests
import re
import os
import zipfile
import glob

class DWDDataImporter:
    def __init__(self, download_dir="data", extract_dir="data/unzipped"):
        self.dwd_url = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"
        self.download_dir = download_dir
        self.extract_dir = extract_dir

    def get_file_urls(self):
        """
        This function gets all the file urls from the DWD Open Data Server
        """
        response = requests.get(self.dwd_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        pattern = r'href="(tageswerte_KL_.*?\.zip)"'
        file_names = re.findall(pattern, response.text)

        file_urls = [self.dwd_url + file_name for file_name in file_names]
        return file_urls

    def download_files(self, urls, limit=None):
        """
        Downloads files from a list of URLs into a specified directory.
        """
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        files_to_download = urls[:limit] if limit else urls

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

    def unzip_files(self):
        """
        Unzips all .zip files in a directory to an extract directory.
        """
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)

        zip_files = glob.glob(os.path.join(self.download_dir, "*.zip"))
        for zip_file_path in zip_files:
            file_name = os.path.basename(zip_file_path)
            print(f"Unzipping {file_name}...")
            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(self.extract_dir)
                print(f"Successfully unzipped {file_name}")
            except zipfile.BadZipFile:
                print(f"Error: Failed to unzip {file_name}. It might be a corrupted file.")

    def run_import(self, limit=None):
        """
        Runs the full import process: get URLs, download, and unzip.
        """
        print("Starting DWD data import process...")
        file_urls = self.get_file_urls()
        
        print(f"Found {len(file_urls)} files to download.")
        if limit:
            print(f"Download limit is set to {limit} files.")
        
        self.download_files(file_urls, limit=limit)
        print("\nFile download process finished.")

        print("\nStarting to unzip files...")
        self.unzip_files()
        print("\nFile unzipping process finished.")
