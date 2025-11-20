# Objective: Wetteranalyse (Weather Analysis) Application

This document describes the functionality of a full-stack web application for weather analysis. The goal is to provide a comprehensive description that would allow a developer to recreate the application with equivalent functionality, even if the implementation details (e.g., styling, framework choices) differ.

## 1. Core Concept

The application is a single-page dashboard for exploring historical and live weather data. It centers around a map of Germany where users can select locations or specific weather stations to analyze.

## 2. Functional Requirements

### 2.1. Frontend / User Interface

The UI is composed of a sidebar and a main content area.

#### 2.1.1. Sidebar

-   **Station Search:**
    -   An input field allows users to search for weather stations by name or ID.
    -   As the user types, an autocomplete dropdown appears showing matching stations.
    -   The search should support keyboard navigation (up/down arrows, enter to select).
    -   Selecting a station from the search results focuses the application on that station.

-   **Live Weather Display:**
    -   A card displays the current weather for a selected point on the map or a specific station.
    -   It must show: Temperature, Wind Speed, and Humidity.
    -   It should also display the name of the location/station and the timestamp of the data.

-   **Nearest Stations List:**
    -   When a user clicks on the map, this section lists the 5 closest weather stations to that point.
    -   Each list item should show the station's name, ID, and its distance from the clicked point.
    -   Clicking on a station in this list focuses the application on that station.

#### 2.1.2. Main Content Area

-   **Interactive Map:**
    -   A map (e.g., using Leaflet) is displayed, initially centered on Germany.
    -   Users can click anywhere on the map to set a point of interest. This action will:
        1.  Place a marker at the clicked location.
        2.  Trigger the "Live Weather Display" to show data for that location.
        3.  Populate the "Nearest Stations List".
    -   A toggle switch allows the user to show or hide markers for all available weather stations from the database.
    -   Clicking a station marker will focus the application on that station.

-   **Analysis Controls:**
    -   When a station is selected, this section displays the date range for which historical data is available for that station.
    -   It contains controls for the data analysis:
        -   **Start Date:** A date picker.
        -   **End Date:** A date picker.
        -   **Metric:** A dropdown to select the data to analyze (e.g., Average Temperature, Max Temperature, Min Temperature, Precipitation, Humidity).
        -   **Aggregation:** A dropdown to select the time aggregation (Daily, Monthly, Yearly).
    -   An "Analyze" button triggers the data fetching and visualization.

-   **Chart Display:**
    -   A chart (e.g., using Plotly) visualizes the data requested via the analysis controls.
    -   It should display the selected metric over the chosen date range with the specified aggregation.

-   **Historical Data Table:**
    -   A table displays the raw historical data for the selected station and date range.
    -   The columns should include: Period (Date/Month/Year), Average Temp, Max Temp, Min Temp, Precipitation, and Humidity.

### 2.2. Backend / API

The backend is a web API that serves the frontend and provides data endpoints.

-   **`GET /`**: Serves the main `index.html` file of the application.
-   **Static Files**: Serves static assets (CSS, JavaScript).

-   **`GET /api/live_weather`**:
    -   **Parameters:** `lat` (float), `lon` (float).
    -   **Functionality:** Fetches current weather data for the given coordinates from an external API (like Open-Meteo). It should also perform a reverse geocoding lookup to get a human-readable location name.
    -   **Returns:** A JSON object with temperature, humidity, wind speed, timestamp, and location name.

-   **`GET /api/all_stations`**:
    -   **Parameters:** None.
    -   **Functionality:** Retrieves a list of all weather stations from the database.
    -   **Returns:** A JSON object containing a list of all stations, with each station having at least its ID, name, latitude, longitude, and the start/end dates of data availability.

-   **`GET /api/nearest_stations`**:
    -   **Parameters:** `lat` (float), `lon` (float).
    -   **Functionality:** Finds and returns the 5 nearest weather stations from the database to the given coordinates. Distance should be calculated using the Haversine formula.
    -   **Returns:** A JSON object with a list of the 5 nearest stations, including their distance.

-   **`GET /api/historical_data`**:
    -   **Parameters:** `station_id` (int), `start_date` (string), `end_date` (string), `aggregation` (string: "daily", "monthly", or "yearly").
    -   **Functionality:** Queries the database for historical weather records for the given station and date range, aggregated as specified.
    -   **Returns:** A JSON object containing the aggregated historical data rows.

-   **`GET /api/chart_data`**:
    -   **Parameters:** `station_id` (int), `start_date` (string), `end_date` (string), `metric` (string), `aggregation` (string).
    -   **Functionality:** Queries the database for a specific metric for a given station, date range, and aggregation level, formatted specifically for chart generation.
    -   **Returns:** A JSON object containing lists of labels (periods) and values for the chart.

## 3. Data Model

The application relies on a database (e.g., SQLite) with at least two main tables:

1.  **`Station` Table**:
    -   `STATIONS_ID` (Primary Key)
    -   `STATIONSNAME` (Text)
    -   `GEOBREITE` (Float, Latitude)
    -   `GEOLAENGE` (Float, Longitude)
    -   `VON_DATUM` (Date, Start of data recording)
    -   `BIS_DATUM` (Date, End of data recording)

2.  **`produkt_klima_tag` Table** (or similar for daily climate products):
    -   `STATIONS_ID` (Foreign Key to `Station`)
    -   `MESS_DATUM` (Date, Measurement date)
    -   `TMK` (Float, Average Temperature)
    -   `TXK` (Float, Max Temperature)
    -   `TNK` (Float, Min Temperature)
    -   `RSK` (Float, Precipitation)
    -   `UPM` (Float, Humidity)
    -   Values like `-999` are used to represent missing data and should be handled appropriately by the backend.
