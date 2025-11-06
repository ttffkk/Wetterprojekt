import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
from data_ingestion.downloader import Downloader
from data_ingestion.processor import DataProcessor
from data_ingestion.database import Database
from data_ingestion.importer import CsvImporter

if __name__ == '__main__':
    # Load configuration from YAML file
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    source_config = config['source']
    db_config = config['database']

    # 0. Create the database and tables
    db = Database(db_config['path'], source_config['na_value'], source_config['file_encoding'])
    db.create_connection()
    db.create_tables(db_config['sql_file_path'])

    # 1. Instantiate the classes
    downloader = Downloader(url=source_config['url'], download_dir=source_config['download_dir'])
    processor = DataProcessor(source_config['download_dir'], source_config['extract_dir'], source_config['file_encoding'], source_config['na_value'])
    importer = CsvImporter(db)

    # 2. Get all file URLs
    file_urls = downloader.get_file_urls(pattern=source_config['zip_pattern'])

    # 3. Process each file one by one
    for url in file_urls:
        zip_file_path = downloader.download_file(url)
        if zip_file_path:
            csv_file_path = processor.process_file(
                zip_file_path,
                source_config['product_pattern_to_extract'],
                source_config['header_keyword'],
                source_config['delimiter']
            )
            if csv_file_path:
                importer.import_file(csv_file_path, source_config['delimiter'])
                os.remove(csv_file_path)
            os.remove(zip_file_path)

    db.close_connection()


