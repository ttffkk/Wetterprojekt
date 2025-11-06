# DWD Weather Analysis Application

A Python-based web application for analyzing historical weather data from the German Weather Service (DWD).

## Features

*   **Automated Data Import**: Downloads and processes historical weather data directly from the DWD archive.
*   **Database Storage**: Stores weather data in a local SQLite database for efficient access.
*   **Flexible Analysis**: Allows for analysis of weather data based on custom time periods and locations.
*   **Geospatial Analysis**: Interpolates weather data for any address in Germany, even if there is no direct weather station.
*   **Data Visualization**: Presents results in both tabular and graphical formats.

## Getting Started

### Prerequisites

*   Python 3.x
*   pip

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
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the data import process, execute the main application file:

```sh
python app.py
```

This will download the latest data, process it, and store it in the SQLite database located in the `data/` directory.

*(Note: The web interface for this application is still under development.)*

## Project Structure

```
.
├── app.py                  # Main application entry point
├── config.yaml             # Application configuration
├── Create_table.sql        # SQL schema for the database
├── requirements.txt        # Python dependencies
├── wetter/                 # Module for downloading and processing data
│   ├── downloader.py
│   └── processor.py
├── database/               # Module for database interactions
│   ├── database.py
│   └── importer.py
├── tests/                  # Unit and integration tests
└── data/                   # Directory for data files and the database
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
| `path`          | Path to the SQLite database file.                     |
| `sql_file_path` | Path to the SQL script for creating database tables. |
