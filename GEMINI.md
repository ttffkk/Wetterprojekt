# Gemini Project Overview: DWD Weather Analysis Application

## Project Overview

This project is a Python-based web application for analyzing historical weather data from the German Weather Service (DWD). It automates the downloading, processing, and storage of weather data into a local SQLite database. The application allows for flexible analysis of weather data based on custom time periods and locations, including geospatial analysis to interpolate weather data for any address in Germany. The results are presented in both tabular and graphical formats.

**The project is currently planned for a major architectural rework.** Key goals include migrating to a more scalable database, containerizing the application with Docker, refactoring the data ingestion into a background service, and adding map-based visualizations.

**Main Technologies:**

*   **Backend:** Python, Flask
*   **Database:** SQLite (to be replaced with a more robust database)
*   **Libraries:**
    *   `pandas`: For data manipulation and analysis.
    *   `PyYAML`: For application configuration.
    *   `requests`: For downloading data from the DWD server.
    *   `geopy`: For geospatial analysis.
    *   `flasgger`: For OpenAPI documentation.
*   **Planned Technologies:**
    *   **Docker:** For containerization.
    *   **Map library (e.g., OpenLayers, Leaflet.js):** For web map integration.

**Architecture:**

The application is structured into several modules:

*   `data_ingestion`: Contains modules for downloading, processing, and importing data into the database. (This will be refactored into a background service/package).
*   `backend`: Contains the business logic for data analysis.
*   `web`: Contains the Flask web application, including the RESTful API and the web interface.
*   `tests`: Contains unit and integration tests.
*   `data`: Directory for data files and the SQLite database.

**Planned Architecture (Dockerized):**

The application will be deployed as a multi-container application using Docker:
1.  **Database Container:** A dedicated container for the database service.
2.  **Web App Container:** A container running the Flask web application and API.
3.  **Ingestion Service Container:** A separate container for the data ingestion background worker.

## Building and Running

**Key Commands:**

*   **Installation:**
    ```sh
    pip install -r requirements.txt
    ```
*   **Running the data import:**
    ```sh
    flask import-data
    ```
*   **Running the web application:**
    ```sh
    flask run
    ```
*   **Testing:**
    ```sh
    python -m unittest discover
    ```

## Development Conventions

*   **Configuration:** The application is configured via the `config.yaml` file.
*   **Database:** The database schema is defined in `Create_table.sql`. The `data_ingestion/database.py` module handles all database interactions.
*   **Data Processing:** The `data_ingestion` module is responsible for the entire data pipeline, from downloading the raw data to inserting it into the database.
*   **Testing:** The project includes a `tests` directory, indicating that unit and integration tests are part of the development process.

## Otherwise Important information
* Both `tasks.md` and `GEMINI.md` shall always remain local.
* Please inform the User as soon as you think that a new minor or Major Version of the Product can be released and propose a merge with the master branch.
* After finishing every task make a commit with a Good Commit Message. Push every 5-10 commits
* Update the Readme if the Functionality of the Program has changed or something about the installation has changed. 