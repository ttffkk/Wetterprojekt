import unittest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
import sys
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from backend.database import Database

class TestApi(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch('backend.analysis.Analysis.get_live_weather')
    async def test_get_live_weather(self, mock_get_live_weather):
        mock_get_live_weather.return_value = {
            "error": False,
            "latitude": 52.52,
            "longitude": 13.4,
            "station_name": "Berlin",
            "temperature": 15.0,
            "relative_humidity": 60.0,
            "wind_speed_10m": 10.0,
            "rain": 0.0,
            "timestamp": "2025-11-20T12:00:00Z",
        }
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/live_weather?lat=52.52&lon=13.4")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['station_name'], "Berlin")
        self.assertEqual(data['temperature'], 15.0)

    @patch('backend.database.Database.get_all_stations')
    async def test_get_all_stations(self, mock_get_all_stations):
        mock_get_all_stations.return_value = [
            {'station_id': 1, 'station_name': 'Station A'},
            {'station_id': 2, 'station_name': 'Station B'},
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/all_stations")
            
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['stations']), 2)

    @patch('backend.database.Database.get_stations_with_distance')
    async def test_get_nearest_stations(self, mock_get_stations_with_distance):
        mock_get_stations_with_distance.return_value = [
            {'station_id': 1, 'station_name': 'Station A', 'distance_km': 5.0},
        ]

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/nearest_stations?lat=52.52&lon=13.4")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['stations']), 1)
        self.assertEqual(data['stations'][0]['distance_km'], 5.0)

    @patch('backend.database.Database.get_historical_data')
    async def test_get_historical_data(self, mock_get_historical_data):
        mock_get_historical_data.return_value = [
            {'period': '2023', 'avg_temp': 10.0}
        ]

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/historical_data?station_id=1&start_date=2023-01-01&end_date=2023-12-31&aggregation=yearly")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['aggregation'], 'yearly')
        self.assertEqual(len(data['rows']), 1)
        self.assertEqual(data['rows'][0]['period'], '2023')

    @patch('backend.database.Database.get_chart_data')
    async def test_get_chart_data(self, mock_get_chart_data):
        mock_get_chart_data.return_value = [
            {'period': '2023', 'value': 12.0}
        ]

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/api/chart_data?station_id=1&metric=tmk&aggregation=yearly&start_date=2023-01-01&end_date=2023-12-31")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['metric'], 'tmk')
        self.assertEqual(len(data['rows']), 1)
        self.assertEqual(data['rows'][0]['value'], 12.0)


if __name__ == '__main__':
    unittest.main()

