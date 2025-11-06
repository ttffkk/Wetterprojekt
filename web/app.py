import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import click
from flask import Flask, render_template
from data_ingestion.downloader import Downloader
from data_ingestion.processor import DataProcessor
from data_ingestion.database import Database
from data_ingestion.importer import CsvImporter

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.cli.command("import-data")
def import_data_command():
    """Command to import the weather data."""
    import_data()
    click.echo("Data import finished.")

def import_data():
    """Function to import the weather data."""
    # Load configuration from YAML file
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    source_config = config['source']
    patterns_config = source_config['patterns']
    file_properties_config = source_config['file_properties']
    paths_config = source_config['paths']
    db_config = config['database']

    # 0. Create the database and tables
    db = Database(db_config['path'], file_properties_config['na_value'], file_properties_config['file_encoding'])
    db.create_connection()
    db.create_tables(db_config['sql_file_path'])

    # 1. Instantiate the classes
    downloader = Downloader(url=source_config['url'], download_dir=paths_config['download_dir'])
    processor = DataProcessor(paths_config['download_dir'], paths_config['extract_dir'], file_properties_config['file_encoding'], file_properties_config['na_value'])
    importer = CsvImporter(db)

    # 2. Get all file URLs
    file_urls = downloader.get_file_urls(pattern=patterns_config['zip_pattern'])

    # 3. Process each file one by one
    for url in file_urls:
        zip_file_path = downloader.download_file(url)
        if zip_file_path:
            csv_file_path = processor.process_file(
                zip_file_path,
                patterns_config['product_pattern_to_extract'],
                patterns_config['header_keyword'],
                file_properties_config['delimiter']
            )
            if csv_file_path:
                importer.import_file(csv_file_path, file_properties_config['delimiter'])
                os.remove(csv_file_path)
            os.remove(zip_file_path)

    db.close_connection()

if __name__ == '__main__':
    app.run(debug=True)
