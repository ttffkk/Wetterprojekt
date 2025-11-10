import typer
import yaml
from .data_pipeline import DataIngestionPipeline

def main(config_file: str = typer.Option("config.yaml", help="Path to the configuration file.")):
    """
    Command to import the weather data from DWD.
    """
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
    typer.run(main)


