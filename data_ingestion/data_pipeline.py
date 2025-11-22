import os
import re
import zipfile
import time
import logging

import pandas as pd
import requests
import psycopg

from .database import Database


class DataIngestionPipeline:
    def __init__(self, config, logger):
        self.config = config
        self.db = None
        self.logger = logger

    def run(self):
        """Command to import the weather data."""
        start_time = time.time()
        
        source_config = self.config['source']
        patterns_config = source_config['patterns']
        file_properties_config = source_config['file_properties']
        paths_config = source_config['paths']
        db_config = self.config['database']

        # 0. Create the database and tables
        self.db = Database(db_config, file_properties_config['na_value'], file_properties_config['file_encoding'], self.logger)
        self.db.create_connection()
        self.db.create_tables(db_config['sql_file_path'])

        # 1. Instantiate the classes
        downloader = Downloader(url=source_config['url'], download_dir=paths_config['download_dir'], logger=self.logger)
        processor = DataProcessor(paths_config['download_dir'], paths_config['extract_dir'], file_properties_config['file_encoding'], file_properties_config['na_value'], self.logger)
        csv_importer = CsvImporter(self.db, self.logger)
        station_importer = StationImporter(self.db.conn, self.logger)

        downloaded_files_count = 0

        # 2. Download and import station data
        station_file_path = downloader.download_station_file(source_config['station_meta_url'])
        if station_file_path:
            station_importer.import_stations(station_file_path)

        # 3. Get all file URLs
        file_urls = downloader.get_file_urls(pattern=patterns_config['zip_pattern'])

        # 4. Process each file one by one
        for url in file_urls:
            zip_file_path, is_newly_downloaded = downloader.download_file(url)
            if is_newly_downloaded:
                downloaded_files_count += 1
            if zip_file_path:
                csv_file_path = processor.process_file(
                    zip_file_path,
                    patterns_config['product_pattern_to_extract'],
                    patterns_config['header_keyword'],
                    file_properties_config['delimiter']
                )
                if csv_file_path:
                    csv_importer.import_file(csv_file_path, file_properties_config['delimiter'])
                    os.remove(csv_file_path)
                os.remove(zip_file_path)

        self.db.close_connection()

        end_time = time.time()
        total_time = end_time - start_time
        self.logger.info(f"Ingestion process finished. Downloaded and processed {downloaded_files_count} new files in {total_time:.2f} seconds.")

class Downloader:
    """Handles downloading data files from a given URL."""
    def __init__(self, url, download_dir, logger):
        self.url = url
        self.download_dir = download_dir
        self.logger = logger

    def get_file_urls(self, pattern):
        """Gets all the file urls from the server that match the pattern."""
        self.logger.info(f"Fetching file list from {self.url}...")
        response = requests.get(self.url)
        response.raise_for_status()

        file_names = re.findall(pattern, response.text)
        file_urls = [self.url + file_name for file_name in file_names]
        self.logger.info(f"Found {len(file_urls)} files matching the pattern.")
        return file_urls

    def download_file(self, url):
        """Downloads a single file from a URL into a specified directory."""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        file_name = url.split('/')[-1]
        local_path = os.path.join(self.download_dir, file_name)

        if os.path.exists(local_path):
            self.logger.info(f"File {file_name} already exists. Skipping.")
            return local_path, False

        self.logger.info(f"Downloading {url}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self.logger.info(f"Successfully downloaded {file_name}")
            return local_path, True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download {url}. Error: {e}")
            return None, False
            
    def download_station_file(self, station_url):
        """Downloads the station description file."""
        self.logger.info("Downloading station description file...")
        path, _ = self.download_file(station_url)
        return path

class CsvImporter:
    def __init__(self, db: Database, logger):
        self.db = db
        self.logger = logger

    def import_file(self, file_path, delimiter):
        """
        Uses an existing database connection to insert a single CSV file.
        """
        self.logger.info("--- Running CSV Importer ---")
        if not self.db.conn:
            self.logger.error("Database connection is not available. Aborting import.")
            return

        try:
            self.logger.info(f"Importing '{os.path.basename(file_path)}'...")
            self.db.insert_csv(file_path, delimiter)
            self.logger.info("CSV import process finished.")

        except Exception as e:
            self.logger.error(f"An unexpected error occurred during CSV import: {e}")

class StationImporter:
    def __init__(self, db_connection, logger):
        self.db_connection = db_connection
        self.logger = logger

    def import_stations(self, file_path):
        """
        Imports station data from the description file into the database.
        """
        self.logger.info(f"Importing stations from {file_path}...")
        
        # Define column widths and names from the source file
        col_specs = [
            (0, 5), (6, 14), (15, 23), (24, 38), (43, 51), 
            (53, 61), (61, 102), (102, 124)
        ]
        source_col_names = [
            "Station_ID", "von_datum", "bis_datum", "Stattionhoehe", 
            "geoBreite", "geoLaenge", "Stationsname", "Bundesland"
        ]

        try:
            # Read the fixed-width file
            df = pd.read_fwf(file_path, colspecs=col_specs, names=source_col_names, skiprows=2, encoding='latin-1', dtype=str)

            # --- Data Cleaning and Transformation ---
            df.rename(columns={
                "Station_ID": "station_id",
                "von_datum": "start_date",
                "bis_datum": "end_date",
                "Stattionhoehe": "altitude",
                "geoBreite": "latitude",
                "geoLaenge": "longitude",
                "Stationsname": "station_name",
                "Bundesland": "state"
            }, inplace=True)

            df['station_name'] = df['station_name'].str.strip()
            df['state'] = df['state'].str.strip()
            
            # Convert data types
            df['station_id'] = pd.to_numeric(df['station_id'], errors='coerce')
            df['start_date'] = pd.to_datetime(df['start_date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
            df['end_date'] = pd.to_datetime(df['end_date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
            df['altitude'] = pd.to_numeric(df['altitude'], errors='coerce')
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

            # Drop rows with invalid station_id
df = df.dropna(subset=['station_id'])
            df['station_id'] = df['station_id'].astype(int)

            # --- Database Insertion ---
            with self.db_connection.cursor() as cur:
                for _, row in df.iterrows():
                    try:
                        cur.execute(
                            """
                            INSERT INTO stations (station_id, start_date, end_date, altitude, latitude, longitude, station_name, state)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (station_id) DO NOTHING
                            """,
                            (row['station_id'], row['start_date'], row['end_date'], row['altitude'], row['latitude'], row['longitude'], row['station_name'], row['state'])
                        )
                    except Exception as e:
                        self.logger.warning(f"Skipping duplicate or invalid station {row['station_id']}: {e}")
            
            self.db_connection.commit()
            self.logger.info(f"Successfully imported {len(df)} stations.")

        except FileNotFoundError:
            self.logger.error(f"Error: Station description file not found at {file_path}")
        except Exception as e:
            self.logger.error(f"An error occurred during station import: {e}")

class DataProcessor:
    """Handles unzipping, filtering, and parsing of data files."""
    def __init__(self, download_dir, extract_dir, file_encoding, na_value, logger):
        self.download_dir = download_dir
        self.extract_dir = extract_dir
        self.file_encoding = file_encoding
        self.na_value = na_value
        self.logger = logger

    def process_file(self, zip_file_path, file_pattern_to_extract, header_keyword, delimiter):
        """Processes a single zip file: unzips, parses, and renames to CSV."""
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)

        file_name = os.path.basename(zip_file_path)
        self.logger.info(f"Processing {file_name}...")
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_dir)
                self.logger.info(f"  - Extracted all files from {file_name}")

                product_file = None
                for file_in_zip in zip_ref.namelist():
                    if file_pattern_to_extract in file_in_zip:
                        product_file = file_in_zip
                        break
                
                if product_file:
                    extracted_file_path = os.path.join(self.extract_dir, product_file)
                else:
                    self.logger.warning(f"  - Warning: No file matching '{file_pattern_to_extract}' found in {file_name}")
                    return None

            header_line_index = self._find_header_line(extracted_file_path, header_keyword)
            if header_line_index is None:
                self.logger.warning(f"  - Warning: Could not find header row in {os.path.basename(extracted_file_path)}. Skipping.")
                return None

            df = pd.read_csv(
                extracted_file_path,
                delimiter=delimiter,
                encoding=self.file_encoding,
                skiprows=header_line_index
            )

            df.columns = df.columns.str.strip()
            df.replace(self.na_value, pd.NA, inplace=True)

            if extracted_file_path.endswith('.txt'):
                new_file_path = os.path.splitext(extracted_file_path)[0] + ".csv"
                df.to_csv(new_file_path, index=False, sep=delimiter)
                self.logger.info(f"  - Renamed to {os.path.basename(new_file_path)}")
                os.remove(extracted_file_path)
                return new_file_path
            else:
                df.to_csv(extracted_file_path, index=False, sep=delimiter)
                return extracted_file_path

        except zipfile.BadZipFile:
            self.logger.error(f"Error: Failed to unzip {file_name}. It might be a corrupted file.")
            return None
        except OSError as e:
            self.logger.error(f"Error processing file {file_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"  - Error parsing file {os.path.basename(zip_file_path)}: {e}")
            return None

    def _find_header_line(self, file_path, header_keyword):
        """Finds the line number of the header in a data file."""
        with open(file_path, 'r', encoding=self.file_encoding) as f:
            for i, line in enumerate(f):
                if header_keyword in line:
                    return i
        return None
