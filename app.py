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
    db = Database(db_config['path'])
    db.create_connection()
    db.create_tables()

    # 1. Download the data
    downloader = Downloader(url=source_config['url'])
    downloader.run(pattern=source_config['zip_pattern'])  # Using a limit for demonstration

    # 2. Process the downloaded data
    processor = DataProcessor()
    processed_data = processor.run(
        file_pattern_to_extract=source_config['product_pattern_to_extract'],
        file_glob=source_config['data_file_glob'],
        header_keyword=source_config['header_keyword'],
        delimiter=source_config['delimiter']
    )

    # 3. Import the processed data into the database
    importer = CsvImporter(db)
    importer.run()


    db.close_connection()


