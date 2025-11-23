# DWD Weather Analysis Application

A Python-based web application for analyzing historical weather data from the German Weather Service (DWD), fully containerized with Docker.

## Features

*   **Automated Data Import**: Downloads and processes historical weather data directly from the DWD's open data server.
*   **PostgreSQL Database**: Stores weather data in a robust PostgreSQL database for efficient querying and analysis.
*   **Geospatial Analysis**: Interpolates weather data for any address in Germany using the nearest weather stations.
*   **Flexible Analysis**: Provides endpoints for analyzing weather data by custom time periods and locations.
*   **Data Visualization**: Generates temperature plots for specified locations and date ranges.
*   **RESTful API**: A modern, interactive API built with FastAPI, with automatic documentation.
*   **Modern Frontend**: A Vue.js-based frontend for interacting with the API.
*   **Dockerized Environment**: Comes with a complete Docker setup for easy deployment and consistent development environments.

## Getting Started with Docker

This is the recommended way to run the application.

### Prerequisites

*   Docker
*   Docker Compose

### Installation & Usage

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/ttffkk/Wetterprojekt.git
    cd Wetterprojekt
    ```

2.  **Build and run the services:**
    This command will build the Docker images for the web and ingestion services, and start the web server and the PostgreSQL database.
    ```sh
    docker-compose up --build -d
    ```
    The `-d` flag runs the containers in detached mode.

4.  **Run the Data Import:**
    With the services running, execute the data ingestion process. This will connect to the database inside the Docker network and start downloading and importing the weather data. This process can take a long time.
    ```sh
    docker-compose run --rm ingestion
    ```

5.  **Access the Application:**
    *   **Web Interface**: `http://localhost:8080`
    *   **API Docs (Swagger UI)**: `http://localhost:8000/docs`

## Project Structure

```
.
├── backend/
│   └── analysis.py
├── data_ingestion/
│   ├── __init__.py
│   ├── cli.py
│   ├── data_pipeline.py
│   └── database.py
├── web/
│   ├── __init__.py
│   └── routers.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── .gitignore
├── config.yaml
├── Create_table.sql
├── Dockerfile
├── Dockerfile.ingestion
├── docker-compose.yml
├── main.py
├── README.md
├── requirements.txt
└── setup.py
```

## Configuration

The application is configured using environment variables. The values in `docker-compose.yml` override the database settings.
