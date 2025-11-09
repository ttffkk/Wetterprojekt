import typer
import yaml
import os
from data_ingestion.data_pipeline import Downloader, DataProcessor, CsvImporter, ParameterImporter, StationImporter
from data_ingestion.database import Database

app = typer.Typer()

@app.command()
def import_data():
    """Command to import the weather data."""
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
    csv_importer = CsvImporter(db)
    station_importer = StationImporter(db.conn)
    parameter_importer = ParameterImporter(db)

    # 2. Download and import station data
    station_file_path = downloader.download_station_file(source_config['station_meta_url'])
    if station_file_path:
        station_importer.import_stations(station_file_path)

    # 3. Get all file URLs
    file_urls = downloader.get_file_urls(pattern=patterns_config['zip_pattern'])

    # 4. Process each file one by one
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
                csv_importer.import_file(csv_file_path, file_properties_config['delimiter'])
                os.remove(csv_file_path)
            os.remove(zip_file_path)

    # 5. Import parameter descriptions
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
        parameter_importer.import_parameters(metadata_file)
    else:
        typer.echo("Metadata file for parameters not found. Please make sure at least one data archive is extracted.")

    db.close_connection()
    typer.echo("Data import finished.")

if __name__ == "__main__":
    app()
