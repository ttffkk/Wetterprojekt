import requests
import re
import os
import zipfile
import glob
import pandas as pd
import csv
import sqlite3

from .database import Database # Assuming Database class is in data_ingestion/database.py

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

class StationImporter:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def import_stations(self, file_path):
        """
        Imports station data from the description file into the database.
        """
        print(f"Importing stations from {file_path}...")
        
        # Define column widths and names
        col_specs = [
            (0, 5), (6, 14), (15, 23), (24, 38), (43, 51), 
            (53, 61), (61, 102), (102, 124)
        ]
        col_names = [
            "Station_ID", "von_datum", "bis_datum", "Stattionhoehe", 
            "geoBreite", "geoLaenge", "Stationsname", "Bundesland"
        ]

        try:
            # Read the fixed-width file, skipping header rows
            df = pd.read_fwf(file_path, colspecs=col_specs, names=col_names, skiprows=2, encoding='latin-1', dtype=str)

            # The 'Abgabe' column is not well-structured, so we'll ignore it for now
            # as it's not critical for the main functionality.

            # Clean up the data
            df['Stationsname'] = df['Stationsname'].str.strip()
            df['Bundesland'] = df['Bundesland'].str.strip()
            
            # Convert data types
            df['Station_ID'] = pd.to_numeric(df['Station_ID'], errors='coerce')
            df['von_datum'] = pd.to_datetime(df['von_datum'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
            df['bis_datum'] = pd.to_datetime(df['bis_datum'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
            df['Stattionhoehe'] = pd.to_numeric(df['Stattionhoehe'], errors='coerce')
            df['geoBreite'] = pd.to_numeric(df['geoBreite'], errors='coerce')
            df['geoLaenge'] = pd.to_numeric(df['geoLaenge'], errors='coerce')

            # Drop rows with invalid Station_ID
            df.dropna(subset=['Station_ID'], inplace=True)
            df['Station_ID'] = df['Station_ID'].astype(int)

            # Insert data into the database
            cursor = self.db_connection.cursor()
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO Station (Station_ID, von_datum, bis_datum, Stattionhoehe, geoBreite, geoLaenge, Stationsname, Bundesland)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (row['Station_ID'], row['von_datum'], row['bis_datum'], row['Stattionhoehe'], row['geoBreite'], row['geoLaenge'], row['Stationsname'], row['Bundesland'])
                    )
                except Exception as e:
                    # This will catch primary key conflicts and other insertion errors
                    print(f"Skipping duplicate or invalid station {row['Station_ID']}: {e}")
            
            self.db_connection.commit()
            print(f"Successfully imported {len(df)} stations.")

        except FileNotFoundError:
            print(f"Error: Station description file not found at {file_path}")
        except Exception as e:
            print(f"An error occurred during station import: {e}")

class DataProcessor:
    """Handles unzipping, filtering, and parsing of data files."""
    def __init__(self, download_dir, extract_dir, file_encoding, na_value):
        self.download_dir = download_dir
        self.extract_dir = extract_dir
        self.file_encoding = file_encoding
        self.na_value = na_value

    def process_file(self, zip_file_path, file_pattern_to_extract, header_keyword, delimiter):
        """Processes a single zip file: unzips, parses, and renames to CSV."""
        if not os.path.exists(self.extract_dir):
            os.makedirs(self.extract_dir)

        file_name = os.path.basename(zip_file_path)
        print(f"Processing {file_name}...")
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                product_file = None
                for file_in_zip in zip_ref.namelist():
                    if file_pattern_to_extract in file_in_zip:
                        product_file = file_in_zip
                        break
                
                if product_file:
                    extracted_file_path = zip_ref.extract(product_file, self.extract_dir)
                    print(f"  - Extracted: {product_file}")
                else:
                    print(f"  - Warning: No file matching '{file_pattern_to_extract}' found in {file_name}")
                    return None

            header_line_index = self._find_header_line(extracted_file_path, header_keyword)
            if header_line_index is None:
                print(f"  - Warning: Could not find header row in {os.path.basename(extracted_file_path)}. Skipping.")
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
                # Write the dataframe to a new csv file
                df.to_csv(new_file_path, index=False, sep=delimiter)
                print(f"  - Renamed to {os.path.basename(new_file_path)}")
                os.remove(extracted_file_path)
                return new_file_path
            else:
                # if it is already a csv, we just overwrite it with the cleaned data
                df.to_csv(extracted_file_path, index=False, sep=delimiter)
                return extracted_file_path

        except zipfile.BadZipFile:
            print(f"Error: Failed to unzip {file_name}. It might be a corrupted file.")
            return None
        except OSError as e:
            print(f"Error processing file {file_name}: {e}")
            return None
        except Exception as e:
            print(f"  - Error parsing file {os.path.basename(zip_file_path)}: {e}")
            return None

    def _find_header_line(self, file_path, header_keyword):
        """Finds the line number of the header in a data file."""
        with open(file_path, 'r', encoding=self.file_encoding) as f:
            for i, line in enumerate(f):
                if header_keyword in line:
                    return i
        return None