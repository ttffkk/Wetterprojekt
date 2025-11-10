from setuptools import setup, find_packages

setup(
    name='dwd_data_ingestion',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
        'psycopg2-binary',
        'typer',
    ],
    entry_points={
        'console_scripts': [
            'dwd-ingest=dwd_data_ingestion.cli:main',
        ],
    },
)
