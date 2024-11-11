import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from services.weather import get_weather

class TestWeatherFunctions(unittest.TestCase):

    @patch('services.weather.requests.get')
    def test_get_weather_success(self, mock_get):
        # Mock successful OpenWeather API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {"dt_txt": "2024-12-25 12:00:00", "weather": [{"description": "clear sky"}], "main": {"temp": 5.0}},
                {"dt_txt": "2024-12-25 15:00:00", "weather": [{"description": "few clouds"}], "main": {"temp": 7.0}},
                {"dt_txt": "2024-12-26 12:00:00", "weather": [{"description": "rain"}], "main": {"temp": 4.0}},
            ]
        }
        mock_get.return_value = mock_response

        # Define the start and end dates for filtering
        start_date = datetime(2024, 12, 25, 0, 0, 0)
        end_date = datetime(2024, 12, 26, 23, 59, 59)

        # Call the function and check the result
        result = get_weather("Paris", start_date, end_date)
        expected_result = [
            "December 25th: clear sky, 6.00 °C",
            "December 26th: rain, 4.00 °C"
        ]
        self.assertEqual(result, expected_result)

    @patch('services.weather.requests.get')
    def test_get_weather_no_data_within_range(self, mock_get):
        # Mock response where data is outside the specified date range
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {"dt_txt": "2024-12-24 12:00:00", "weather": [{"description": "snow"}], "main": {"temp": -2.0}},
            ]
        }
        mock_get.return_value = mock_response

        # Define a date range where there's no data
        start_date = datetime(2024, 12, 25, 0, 0, 0)
        end_date = datetime(2024, 12, 26, 23, 59, 59)

        # Call the function and check that the result is empty
        result = get_weather("Paris", start_date, end_date)
        self.assertEqual(result, [])

    @patch('services.weather.requests.get')
    def test_get_weather_api_error(self, mock_get):
        # Mock a failed API response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Define the date range
        start_date = datetime(2024, 12, 25, 0, 0, 0)
        end_date = datetime(2024, 12, 26, 23, 59, 59)

        # Check that an exception is raised for API error
        with self.assertRaises(Exception) as context:
            get_weather("UnknownCity", start_date, end_date)
        self.assertIn("Failed to fetch weather data for UnknownCity", str(context.exception))

    @patch('services.weather.requests.get')
    def test_get_weather_date_suffix(self, mock_get):
        # Test date suffix formatting (e.g., "1st", "2nd", "3rd", "4th", etc.)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {"dt_txt": "2024-12-21 12:00:00", "weather": [{"description": "clear sky"}], "main": {"temp": 8.0}},
                {"dt_txt": "2024-12-22 12:00:00", "weather": [{"description": "cloudy"}], "main": {"temp": 6.0}},
                {"dt_txt": "2024-12-23 12:00:00", "weather": [{"description": "rain"}], "main": {"temp": 5.0}},
                {"dt_txt": "2024-12-31 12:00:00", "weather": [{"description": "snow"}], "main": {"temp": -1.0}},
            ]
        }
        mock_get.return_value = mock_response

        # Define the start and end dates for filtering
        start_date = datetime(2024, 12, 21, 0, 0, 0)
        end_date = datetime(2024, 12, 31, 23, 59, 59)

        # Call the function and check the result
        result = get_weather("Paris", start_date, end_date)
        expected_result = [
            "December 21st: clear sky, 8.00 °C",
            "December 22nd: cloudy, 6.00 °C",
            "December 23rd: rain, 5.00 °C",
            "December 31st: snow, -1.00 °C",
        ]
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
