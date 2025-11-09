import typer
import yaml
from dwd_data_ingestion.data_pipeline import DataIngestionPipeline

app = typer.Typer()

@app.command()
def import_data(config_file: str = 'config.yaml'):
    """Command to import the weather data."""
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    pipeline = DataIngestionPipeline(config)
    pipeline.run()

    typer.echo("Data import finished.")

if __name__ == "__main__":
    app()

