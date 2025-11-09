from celery import Celery

app = Celery('dwd_data_ingestion',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['dwd_data_ingestion.tasks'])

if __name__ == '__main__':
    app.start()
