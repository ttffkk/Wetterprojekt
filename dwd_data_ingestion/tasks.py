from dwd_data_ingestion.celery import app
from dwd_data_ingestion.data_pipeline import DataIngestionPipeline
import yaml

@app.task
def import_data_task(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    pipeline = DataIngestionPipeline(config)
    pipeline.run()
