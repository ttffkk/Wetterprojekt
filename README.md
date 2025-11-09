# DWD Weather Analysis Application

A Python-based web application for analyzing historical weather data from the German Weather Service (DWD).

## Features

*   **Automated Data Import**: Downloads and processes historical weather data directly from the DWD archive.
*   **Database Storage**: Stores weather data in a PostgreSQL database for efficient access.
*   **Flexible Analysis**: Allows for analysis of weather data based on custom time periods and locations.
*   **Geospatial Analysis**: Interpolates weather data for any address in Germany, even if there is no direct weather station.
*   **Data Aggregation**: Calculates daily mean temperature and aggregates data by month and year.
*   **Data Visualization**: Presents results in both tabular and graphical formats, including temperature plots.
*   **RESTful API**: Provides a RESTful API for accessing weather data and generating plots.

## Roadmap

The project is currently undergoing a major rework to improve its architecture, scalability, and feature set. Here are the key areas of development:

*   **Database Migration**: The current SQLite database will be migrated to PostgreSQL to handle larger datasets and more complex queries.
*   **Data Ingestion as a Package**: The data ingestion process will be refactored into a standalone Python package with background processing capabilities for more efficient and non-blocking data downloads.
*   **Dockerization**: The entire application will be containerized using Docker with a multi-container setup:
    *   A container for the database.
    *   A container for the web application.
    *   A dedicated container for the data ingestion service.
*   **Map Integration**: The web interface will be enhanced with map visualization using OpenStreet Maps or Google Maps to display weather station locations.
*   **Station Data**: The application will be updated to download and store metadata for all available weather stations, not just the ones in the immediate vicinity of a query.

## Getting Started

### Prerequisites

*   Python 3.x
*   pip
*   PostgreSQL

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/ttffkk/Wetterprojekt.git
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    *   On Windows:
        ```sh
        python -m venv .venv
        .venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```sh
        python -m venv .venv
        source .venv/bin/activate
        ```

3.  **Install the required packages:**

    This will install Flask, Pandas, and other necessary packages.
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Data Import

To run the data import process, execute the following command:

```sh
flask import-data
```

This will download the latest data, process it, and store it in the PostgreSQL database.

### Web Application

To run the web application, execute the following command:

```sh
flask run
```

This will start a local development server. You can access the application by navigating to `http://127.0.0.1:5000` in your web browser.

## Project Structure

```
.
├── .gitignore
├── config.yaml
├── Create_table.sql
├── README.md
├── requirements.txt
├── backend/
│   └── analysis.py
├── data/
├── data_ingestion/
│   ├── database.py
│   ├── downloader.py
│   ├── importer.py
│   └── processor.py
├── tests/
│   ├── test_analysis.py
│   ├── test_downloader.py
│   └── test_processor.py
└── web/
    └── app.py
```

## Configuration

The application is configured via the `config.yaml` file. Here is a description of the variables:

### `source`

| Variable                     | Description                                                                 |
| ---------------------------- | --------------------------------------------------------------------------- |
| `url`                        | Base URL for downloading historical weather data from the DWD.              |
| `zip_pattern`                | Regex pattern to find zip file names on the DWD server listing.             |
| `product_pattern_to_extract` | Keyword to identify the actual product file within a zip archive.           |
| `data_file_glob`             | Glob pattern for data files after extraction (e.g., "produkt_*.txt").       |
| `header_keyword`             | Keyword to find the header line in the raw data files.                      |
| `delimiter`                  | Delimiter used in the raw data files (e.g., ';', ',').                      |
| `file_encoding`              | Encoding of the raw data files.                                             |
| `na_value`                   | Value representing 'Not Available' or missing data in the raw files.        |
| `download_dir`               | Directory where raw zip files are downloaded.                               |
| `extract_dir`                | Directory where data files are extracted from zip archives.                 |
| `zip_glob`                   | Glob pattern to find zip files in the download directory.                   |

### `database`

| Variable        | Description                                           |
| --------------- | ----------------------------------------------------- |
| `host`          | The hostname of the PostgreSQL server.                |
| `port`          | The port of the PostgreSQL server.                    |
| `user`          | The username for the database connection.             |
| `password`      | The password for the database connection.             |
| `dbname`        | The name of the database to connect to.               |
| `sql_file_path` | Path to the SQL script for creating database tables. |
