# DWD Weather Analysis Application

A Python-based web application for analyzing historical weather data from the German Weather Service (DWD), fully containerized with Docker.

## Features

*   **Automated Data Import**: Downloads and processes historical weather data directly from the DWD's open data server.
*   **PostgreSQL Database**: Stores weather data in a robust PostgreSQL database for efficient querying and analysis.
*   **Geospatial Analysis**: Interpolates weather data for any address in Germany using the nearest weather stations.
*   **Flexible Analysis**: Provides endpoints for analyzing weather data by custom time periods and locations.
*   **Data Visualization**: Generates temperature plots for specified locations and date ranges.
*   **RESTful API**: A modern, interactive API built with FastAPI, with automatic documentation.
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

2.  **Configure your environment:**
    Create a `.env` file by copying the example file. This file will hold your database credentials.
    ```sh
    cp .env.example .env
    ```
    You can modify the values in `.env` if needed, but the defaults are set up to work with Docker Compose out of the box.

3.  **Build and run the services:**
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
    *   **Web Interface**: `http://localhost:8000`
    *   **API Docs (Swagger UI)**: `http://localhost:8000/docs`

## Local Development Setup

If you prefer to run the application without Docker, follow these steps.

### Prerequisites

*   Python 3.9+
*   A running PostgreSQL server

### Installation

1.  **Clone the repository and navigate into it.**

2.  **Create and activate a Python virtual environment:**
    ```sh
    python -m venv .venv
    # On Windows: .venv\Scripts\activate
    # On macOS/Linux: source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure the database:**
    *   Ensure your PostgreSQL server is running.
    *   Create a database (e.g., `wetter`).
    *   Edit the `database` section in `config.yaml` with your connection details (host, port, user, password, dbname).

### Usage

1.  **Run the Data Import:**
    This command uses the credentials from your `config.yaml` to connect to the database.
    ```sh
    dwd-ingest import-data
    ```

2.  **Run the Web Application:**
    ```sh
    uvicorn main:app --reload
    ```
    The application will be available at `http://localhost:8000`.

## Project Structure

```
.
├── backend/
│   └── analysis.py
├── dwd_data_ingestion/
│   ├── __init__.py
│   ├── cli.py
│   ├── data_pipeline.py
│   └── database.py
├── web/
│   ├── __init__.py
│   ├── routers.py
│   └── templates/
│       └── index.html
├── .env.example
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

The application can be configured in two ways depending on the environment:

*   **`config.yaml`**: Used for local development when not using Docker. It contains settings for the data source and database connection.
*   **`.env` file**: Used for Docker deployments. The values in this file override the database settings in `config.yaml`. The `docker-compose.yml` file reads this file to configure the services.