import yaml
from wetter.downloader import Downloader
from wetter.processor import DataProcessor
from database.database import Database
from database.importer import CsvImporter

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

    # 1. Download the data
    downloader = Downloader(url=source_config['url'], download_dir=source_config['download_dir'])
    downloader.run(pattern=source_config['zip_pattern'])  # Using a limit for demonstration

    # 2. Process the downloaded data
    processor = DataProcessor(source_config['download_dir'], source_config['extract_dir'], source_config['file_encoding'], source_config['na_value'])
    processed_data = processor.run(
        file_pattern_to_extract=source_config['product_pattern_to_extract'],
        file_glob=source_config['data_file_glob'],
        header_keyword=source_config['header_keyword'],
        delimiter=source_config['delimiter'],
        zip_glob=source_config['zip_glob']
    )

    # 3. Import the processed data into the database
    importer = CsvImporter(db, source_config['extract_dir'])
    importer.run(source_config['delimiter'])


    db.close_connection()


