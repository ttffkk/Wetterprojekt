from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from data_ingestion.database import Database
import pandas as pd

class Analysis:
    def __init__(self, db: Database):
        self.db = db
        self.geolocator = Nominatim(user_agent="wetterprojekt")

    @staticmethod
    def calculate_distance(coord1, coord2):
        """Calculates the distance between two coordinates in kilometers."""
        return geodesic(coord1, coord2).kilometers

    def find_nearest_stations(self, address: str, num_stations: int = 5):
        """
        Find the nearest weather stations to a given address.

        :param address: The address to geocode.
        :param num_stations: The number of nearest stations to return.
        :return: A list of tuples containing (station_id, name, distance_km).
        """
        try:
            location = self.geolocator.geocode(address)
            if not location:
                print(f"Error: Could not geocode address '{address}'.")
                return []
        except Exception as e:
            print(f"An error occurred during geocoding: {e}")
            return []

        target_coords = (location.latitude, location.longitude)
        all_stations = self.db.get_all_stations()

        stations_with_distance = []
        for station in all_stations:
            station_id, lat, lon, name = station
            if lat is None or lon is None:
                continue
            station_coords = (lat, lon)
            distance = self.calculate_distance(target_coords, station_coords)
            stations_with_distance.append((station_id, name, distance))

        # Sort stations by distance
        stations_with_distance.sort(key=lambda x: x[2])

        return stations_with_distance[:num_stations]

    def interpolate_weather_data(self, address: str, date: str):
        """
        Interpolate weather data for a given address and date.

        :param address: The address to interpolate data for.
        :param date: The date for which to interpolate data ('YYYY-MM-DD').
        :return: The interpolated temperature.
        """
        nearest_stations = self.find_nearest_stations(address)
        if not nearest_stations:
            return None

        station_data = []
        for station_id, name, distance in nearest_stations:
            weather_data = self.db.get_weather_data(station_id, date)
            if weather_data and weather_data.get('TMK') is not None:
                station_data.append({
                    'distance': distance,
                    'temperature': weather_data['TMK']
                })

        if not station_data:
            print("No weather data available for the nearest stations on the given date.")
            return None

        # Inverse Distance Weighting
        total_weight = 0
        weighted_sum = 0
        for data in station_data:
            if data['distance'] == 0: # If the location is at a station, return its temperature
                return data['temperature']
            weight = 1 / data['distance']
            weighted_sum += weight * data['temperature']
            total_weight += weight

        if total_weight == 0:
            return None

        return weighted_sum / total_weight