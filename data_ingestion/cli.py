import typer
import yaml
import logging
from .data_pipeline import DataIngestionPipeline

app = typer.Typer()

@app.command()
def main(
    config_file: str = typer.Option("config.yaml", help="Path to the configuration file."),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging.")
):
    """
    Command to import the weather data from DWD.
    """
    # Setup logging
    log_level = logging.INFO if debug else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        typer.echo(f"Error: Configuration file '{config_file}' not found.")
        raise typer.Exit(code=1)
    except yaml.YAMLError as e:
        typer.echo(f"Error: Failed to parse configuration file '{config_file}': {e}")
        raise typer.Exit(code=1)

    pipeline = DataIngestionPipeline(config, logger)
    pipeline.run()

    logger.info("Data import finished.")

if __name__ == "__main__":
    app()