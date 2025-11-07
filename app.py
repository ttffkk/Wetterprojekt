import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import yaml
import click
from flask import Flask
from flasgger import Swagger
from web.views import web_blueprint # Import the blueprint
from data_ingestion.downloader import Downloader
from data_ingestion.processor import DataProcessor
from data_ingestion.database import Database
from data_ingestion.importer import CsvImporter, ParameterImporter

app = Flask(__name__, template_folder='web/templates')

app.config['SWAGGER'] = {
    'title': 'DWD Weather Analysis API',
    'uiversion': 3,
    "specs_route": "/api/docs/"
}
swagger = Swagger(app)


app.register_blueprint(web_blueprint) # Register the blueprint

@app.cli.command("import-data")
def import_data_command():
    """Command to import the weather data."""
    import_data()
    click.echo("Data import finished.")

@app.cli.command("import-parameters")
def import_parameters_command():
    """Command to import the parameter descriptions."""
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    db_config = config['database']
    paths_config = config['source']['paths']
    file_properties_config = config['source']['file_properties']

    db = Database(db_config['path'], file_properties_config['na_value'], file_properties_config['file_encoding'])
    db.create_connection()
    
    # The metadata file is expected to be in the archive_dir
    # We will assume one of the zip files has been extracted and the metadata file is present
    # A more robust solution would be to download and extract the metadata file specifically
    
    # Find the metadata file in the extract_dir
    extract_dir = paths_config['extract_dir']
    metadata_file = None
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.startswith('Metadaten_Parameter'):
                metadata_file = os.path.join(root, file)
                break
        if metadata_file:
            break
    
    if metadata_file:
        importer = ParameterImporter(db)
        importer.import_parameters(metadata_file)
    else:
        click.echo("Metadata file not found. Please make sure at least one data archive is extracted.")
    
    db.close_connection()
    click.echo("Parameter import finished.")

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