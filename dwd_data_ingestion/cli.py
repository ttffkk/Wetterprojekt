import typer
from dwd_data_ingestion.tasks import import_data_task

app = typer.Typer()

@app.command()
def import_data(config_file: str = 'config.yaml'):
    """Command to import the weather data."""
    import_data_task.delay(config_file)
    typer.echo("Data import task has been queued.")

if __name__ == "__main__":
    app()

