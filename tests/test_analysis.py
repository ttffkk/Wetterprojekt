import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.analysis import Analysis
from data_ingestion.database import Database

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        """Set up a mock database for testing."""
        self.mock_db = MagicMock(spec=Database)
        self.analysis = Analysis(self.mock_db)

    def test_calculate_distance(self):
        """Test the calculate_distance method."""
        # Coordinates for Berlin and Munich
        berlin_coords = (52.52, 13.40)
        munich_coords = (48.13, 11.57)

        # Test distance between two different points
        distance = self.analysis.calculate_distance(berlin_coords, munich_coords)
        self.assertAlmostEqual(distance, 504, delta=5)  # Allow a 5km tolerance

        # Test distance between the same point (should be 0)
        distance_same = self.analysis.calculate_distance(berlin_coords, berlin_coords)
        self.assertEqual(distance_same, 0)

    @patch('geopy.geocoders.Nominatim')
    def test_find_nearest_stations(self, MockNominatim):
        """Test the find_nearest_stations method."""
        # Mock the geolocator
        mock_geolocator = MockNominatim.return_value
        mock_location = MagicMock()
        mock_location.latitude = 52.52
        mock_location.longitude = 13.40
        mock_geolocator.geocode.return_value = mock_location

        # Mock the database return value
        mock_stations = [
            (1, 52.52, 13.40, 'Berlin-Mitte'),  # 0 km
            (2, 52.53, 13.41, 'Berlin-Prenzlauer Berg'), # approx 1.3 km
            (3, 48.13, 11.57, 'Munich'), # > 500 km
            (4, 53.55, 9.99, 'Hamburg') # > 250 km
        ]
        self.mock_db.get_all_stations.return_value = mock_stations

        # Call the method
        nearest_stations = self.analysis.find_nearest_stations('Berlin, Germany', num_stations=2)

        # Assertions
        self.assertEqual(len(nearest_stations), 2)
        self.assertEqual(nearest_stations[0][0], 1) # Closest is Berlin-Mitte
        self.assertEqual(nearest_stations[1][0], 2) # Second closest is Prenzlauer Berg


if __name__ == '__main__':
    unittest.main()
