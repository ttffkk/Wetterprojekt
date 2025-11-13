| Phase nr | Title | Task Description | Task done? |
|---|---|---|---|
| 8 | API Fix | In `web/routers.py`, correct the `get_db` dependency to properly connect to the PostgreSQL database using the full connection details from `config.yaml`. | ✅ |
| 8 | CLI Fix | In `dwd_data_ingestion/cli.py`, add `try...except` blocks to handle `FileNotFoundError` and `yaml.YAMLError` to prevent the command from crashing if the config file is missing or invalid. | ✅ |
| 8 | Documentation | Update `README.md` with the correct instructions for running the data import (`dwd-ingest import-data`) and starting the web server (`uvicorn main:app --reload`). | ✅ |
| 7 | Rework: Docker | Create a Dockerfile for the web application container. | ✅ |
| 7 | Rework: Docker | Create a Dockerfile for the data ingestion background service. | ✅ |
| 7 | Rework: Docker | Create a `docker-compose.yml` file to manage the multi-container setup (web, database, ingestion). | ✅ |
| 7 | Rework: Web | Integrate a map library (e.g., OpenStreet Maps, Google Maps) into the frontend. | ✅ |
| 7 | Rework: Web | Display weather station locations on the map. | ✅ |
