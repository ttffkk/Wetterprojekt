import requests
from geopy.geocoders import Nominatim
from datetime import datetime, date
from typing import Dict, Any, List

from backend.database import Database

METRIC_LABELS = {
    "tmk": "Mean Temperature (°C)",
    "txk": "Max Temperature (°C)",
    "tnk": "Min Temperature (°C)",
    "rsk": "Precipitation (mm)",
    "upm": "Humidity (%)",
}

class Analysis:
    def __init__(self, db: Database):
        self.db = db
        self.geolocator = Nominatim(user_agent="wetterprojekt_analysis")

    async def get_all_stations(self) -> List[Dict[str, Any]]:
        stations = await self.db.get_all_stations()
        return stations

    async def get_nearest_stations(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        stations = await self.db.get_stations_with_distance(lat, lon, limit=5)
        return stations

    async def get_historical_data(self, station_id: int, start_date: date, end_date: date, aggregation: str) -> List[Dict[str, Any]]:
        metrics = {
            "avg_temp": "AVG(tmk)",
            "max_temp": "MAX(txk)",
            "min_temp": "MIN(tnk)",
            "precipitation": "SUM(rsk)",
            "avg_humidity": "AVG(upm)",
        }
        data = await self.db.get_aggregated_data(station_id, start_date, end_date, aggregation, metrics)
        return data

    async def get_chart_data(self, station_id: int, start_date: date, end_date: date, metric: str, aggregation: str) -> Dict[str, Any]:
        metric_map = {
            "tmk": "AVG(tmk)",
            "txk": "MAX(txk)",
            "tnk": "MIN(tnk)",
            "rsk": "SUM(rsk)",
            "upm": "AVG(upm)",
        }
        if metric.lower() not in metric_map:
            raise ValueError("Invalid metric")

        metrics = {"value": metric_map[metric.lower()]}
        rows = await self.db.get_aggregated_data(station_id, start_date, end_date, aggregation, metrics)
        
        return {
            "metric": metric,
            "metric_label": METRIC_LABELS.get(metric.lower(), "Unknown Metric"),
            "station_id": station_id,
            "aggregation": aggregation,
            "start_date": start_date,
            "end_date": end_date,
            "rows": rows,
        }
