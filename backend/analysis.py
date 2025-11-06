from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from data_ingestion.database import Database

class Analysis:
    def __init__(self, db: Database):
        self.db = db
        self.geolocator = Nominatim(user_agent="wetterprojekt")

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
            distance = geodesic(target_coords, station_coords).kilometers
            stations_with_distance.append((station_id, name, distance))

        # Sort stations by distance
        stations_with_distance.sort(key=lambda x: x[2])

        return stations_with_distance[:num_stations]