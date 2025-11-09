import typer
import yaml
from dwd_data_ingestion.data_pipeline import DataIngestionPipeline

app = typer.Typer()

@app.command()
def import_data(config_file: str = 'config.yaml'):
    """Command to import the weather data."""
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        typer.echo(f"Error: Configuration file '{config_file}' not found.")
        raise typer.Exit(code=1)
    except yaml.YAMLError as e:
        typer.echo(f"Error: Failed to parse configuration file '{config_file}': {e}")
        raise typer.Exit(code=1)

    pipeline = DataIngestionPipeline(config)
    pipeline.run()

    typer.echo("Data import finished.")
if __name__ == "__main__":
    app()

