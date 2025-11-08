| Phase nr | Title               | Task Description                                                                                                                      | Task done? |
|----------|---------------------|---------------------------------------------------------------------------------------------------------------------------------------|------------|
| 1        | Project Setup       | Create initial project structure with folders: `data_ingestion`, `web`, `backend`, `tests`, `data`.                                   | ✅          |
| 1        | Project Setup       | Create initial files: `web/app.py`, `config.yaml`, `Create_table.sql`, `requirements.txt`.                                            | ✅          |
| 1        | Project Setup       | Set up a Python virtual environment and install initial dependencies like Flask and PyYAML.                                           | ✅          |
| 1        | Database            | Define the database schema for weather data in `Create_table.sql`.                                                                    | ✅          |
| 1        | Database            | In `data_ingestion/database.py`, write a function to connect to the SQLite database.                                                  | ✅          |
| 1        | Database            | In `data_ingestion/database.py`, write a function to create the tables based on `Create_table.sql`.                                   | ✅          |
| 2        | Data Import         | In `data_ingestion/downloader.py`, write a function to download a single file from a given URL.                                       | ✅          |
| 2        | Data Import         | In `data_ingestion/downloader.py`, write a function to read URLs from `config.yaml` and download all files into the `data` directory. | ✅          |
| 2        | Data Import         | In `data_ingestion/processor.py`, write a function to read a single downloaded data file.                                             | ✅          |
| 2        | Data Import         | In `data_ingestion/processor.py`, parse the data from the file into a list of dictionaries.                                           | ✅          |
| 2        | Data Import         | In `data_ingestion/importer.py`, write a function to insert a single weather data record into the database.                           | ✅          |
| 2        | Data Import         | In `data_ingestion/importer.py`, add a check to prevent inserting duplicate records.                                                  | ✅          |
| 2        | Data Import         | In `web/app.py`, create a main function to orchestrate the data import process (download, process, import).                           | ✅          |
| 2        | Data Import         | Refactor the data import process to download, unzip, and process one file at a time.                                                  | ✅          |
| 3        | Analysis Engine     | In `backend/analysis.py`, use geopy to add a function to calculate the distance between two coordinates.                              | ✅          |
| 3        | Analysis Engine     | In `backend/analysis.py`, add a function to find the nearest weather stations to a given address.                                     | ✅          |
| 3        | Analysis Engine     | In `backend/analysis.py`, implement a basic interpolation for weather data of a location.                                             | ✅          |
| 3        | Analysis Engine     | In `backend/analysis.py`, add a function to calculate daily mean temperature.                                                         | ✅          |
| 3        | Analysis Engine     | In `backend/analysis.py`, add a function to aggregate data by month (e.g., average temperature).                                      | ✅          |
| 3        | Analysis Engine     | In `backend/analysis.py`, add a function to aggregate data by year (e.g., average temperature).                                       | ✅          |
| 4        | Web Interface       | In `web/app.py`, set up a basic Flask application with a single route for the homepage.                                               | ✅          |
| 4        | Web Interface       | Create a simple HTML template for the homepage with a form for date and location input.                                               | ✅          |
| 4        | Web Interface       | In `web/app.py`, create a RESTful API endpoint to return weather data as JSON.                                                        | ✅          |
| 4        | Web Interface       | Use JavaScript on the frontend to fetch and display the weather data in a table.                                                      | ✅          |
| 4        | Web Interface       | In `web/app.py`, create an endpoint to generate a temperature plot using matplotlib.                                                  | ✅          |
| 4        | Web Interface       | Display the generated plot on the frontend.                                                                                           | ✅          |
| 4        | Web Interface       | In `web/app.py`, create an endpoint to export data to a CSV file.                                                                     | ✅          |
| 4        | Web Interface       | Add a download button for the CSV export on the frontend.                                                                             | ✅          |
| 5        | Testing             | Write a unit test for the file download function in `data_ingestion/downloader.py`.                                                   | ✅          |
| 5        | Testing             | Write a unit test for the data parsing function in `data_ingestion/processor.py`.                                                     | ✅          |
| 5        | Testing             | Write a unit test for the database insertion function in `data_ingestion/importer.py`.                                                | ✅          |
| 5        | Testing             | Write an integration test for the complete data import pipeline.                                                                      | ⬜️          |
| 5        | Testing             | Write a unit test for the analysis functions in `backend/analysis.py`.                                                                | ✅          |
| 5        | Error Handling      | Implement logging in `web/app.py` to log errors and important events.                                                                 | ⬜️          |
| 5        | Error Handling      | Add try-except blocks for file downloads and data parsing to handle potential errors.                                                 | ✅          |
| 5        | Error Handling      | Add try-except blocks for database operations to handle potential errors.                                                             | ✅          |
| 6        | Documentation       | Add docstrings to all functions in the `data_ingestion` module.                                                                       | ⬜️          |
| 6        | Documentation       | Add docstrings to all functions in the `backend` module.                                                                              | ⬜️          |
| 6        | Documentation       | Write a brief user manual in a new `docs/user_manual.md` file.                                                                        | ⬜️          |
| 7        | Rework: Database    | Research and select a new database system (e.g., PostgreSQL, MySQL, etc.).                                                            | ⬜️          |
| 7        | Rework: Database    | Migrate the database schema and data from SQLite to the new system.                                                                   | ⬜️          |
| 7        | Rework: Data Ingestion | Refactor the data ingestion logic into a self-contained, installable Python package.                                               | ⬜️          |
| 7        | Rework: Data Ingestion | Implement a background worker/service for downloading and processing data to prevent blocking the main application.                 | ⬜️          |
| 7        | Rework: Data Ingestion | Implement downloading and storing of DWD station metadata.                                                                          | ⬜️          |
| 7        | Rework: Docker      | Create a Dockerfile for the web application container.                                                                                | ⬜️          |
| 7        | Rework: Docker      | Create a Dockerfile/setup for the new database container.                                                                             | ⬜️          |
| 7        | Rework: Docker      | Create a Dockerfile for the data ingestion background service.                                                                        | ⬜️          |
| 7        | Rework: Docker      | Create a `docker-compose.yml` file to manage the multi-container setup (web, database, ingestion).                                    | ⬜️          |
| 7        | Rework: Web         | Integrate a map library (e.g., OpenStreet Maps, Google Maps) into the frontend.                                                       | ⬜️          |
| 7        | Rework: Web         | Display weather station locations on the map.                                                                                         | ⬜️          |
| 99       | Beauty Patches      | Adjusting empty boxes in Tasks.md into grey checkmark emojis                                                                          | ⬜️          |
| 99       | Beauty Patches      | Prettify config.yml Standard                                                                                                          | ✅          |
| 99       | Beauty Patches      | Update Outdated Packages from requirements.txt                                                                                        | ✅          |
| 99       | Beauty Patches      | Prettify the Logging for Downloading and processing of the Data.                                                                      | ⬜️          |
| 99       | Beauty Patches      | Repackage everything in their dedicated classes and packages                                                                          | ✅          |
| 3.5      | additional Benefits | Add an OpenApi configuration too the Project                                                                                          | ⬜️          |
| 3.5      | additional Benefits | find package that will also host Openapi for the project like swagger                                                                 | ⬜️          |
| 99       | Beauty Patches      | After the downloading of the files, please remove the folder unzipped, since it is empty afterwards.                                  | ⬜️          |