import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from fastapi import HTTPException
from services.flights import (
    get_iata_code,
    get_city_country_from_iata,
    get_flights,
    find_flight_with_smallest_segments,
    format_flight_offer
)

class TestFlightFunctions(unittest.TestCase):

    @patch('services.flights.get_amadeus_client')
    def test_get_iata_code_success(self, mock_get_amadeus_client):
        # Mock Amadeus API response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.result = {"data": [{"iataCode": "JFK"}]}
        mock_client.reference_data.locations.get.return_value = mock_response
        mock_get_amadeus_client.return_value = mock_client

        # Test get_iata_code function
        result = get_iata_code("New York")
        self.assertEqual(result, "JFK")

    @patch('services.flights.get_amadeus_client')
    def test_get_iata_code_not_found(self, mock_get_amadeus_client):
        # Mock 404 response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client.reference_data.locations.get.return_value = mock_response
        mock_get_amadeus_client.return_value = mock_client

        # Test for exception when IATA code is not found
        with self.assertRaises(HTTPException):
            get_iata_code("Unknown City")

    @patch('services.flights.get_amadeus_client')
    def test_get_city_country_from_iata_success(self, mock_get_amadeus_client):
        # Mock response data
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.result = {"data": [{"address": {"cityName": "New York", "countryCode": "US"}}]}
        mock_client.reference_data.locations.get.return_value = mock_response
        mock_get_amadeus_client.return_value = mock_client

        # Test get_city_country_from_iata function
        city, country = get_city_country_from_iata("JFK")
        self.assertEqual(city, "New York")
        self.assertEqual(country, "US")

    @patch('services.flights.get_amadeus_client')
    def test_get_flights(self, mock_get_amadeus_client):
        # Mock flights response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.result = {"data": [{"itineraries": "sample_itineraries"}]}
        mock_client.shopping.flight_offers_search.get.return_value = mock_response
        mock_get_amadeus_client.return_value = mock_client

        # Test get_flights function
        flights = get_flights("JFK", "LAX", "2024-12-25", "2024-12-30")
        self.assertEqual(flights, [{"itineraries": "sample_itineraries"}])

    def test_find_flight_with_smallest_segments(self):
        # Sample flight offers
        flight_offers = [
            {
                "itineraries": [
                    {"segments": [{"departure": {"iataCode": "JFK"}, "arrival": {"iataCode": "LAX"}}]},
                    {"segments": [{"departure": {"iataCode": "LAX"}, "arrival": {"iataCode": "JFK"}}]}
                ]
            },
            {
                "itineraries": [
                    {"segments": [{"departure": {"iataCode": "JFK"}, "arrival": {"iataCode": "LAX"}},
                                  {"departure": {"iataCode": "LAX"}, "arrival": {"iataCode": "SFO"}}]},
                    {"segments": [{"departure": {"iataCode": "SFO"}, "arrival": {"iataCode": "JFK"}}]}
                ]
            }
        ]

        result = find_flight_with_smallest_segments(flight_offers)
        self.assertEqual(len(result["Departure"]), 1)  # Shortest segment for departure
        self.assertEqual(len(result["Return"]), 1)  # Shortest segment for return

    def test_format_flight_offer(self):
        # Sample formatted segments
        shortest_flight = {
            "Departure": [{
                "carrierCode": "AA",
                "number": "100",
                "departure": {"iataCode": "JFK", "at": "2024-12-25T10:00:00"},
                "arrival": {"iataCode": "LAX", "at": "2024-12-25T13:00:00"}
            }],
            "Return": [{
                "carrierCode": "AA",
                "number": "101",
                "departure": {"iataCode": "LAX", "at": "2024-12-30T14:00:00"},
                "arrival": {"iataCode": "JFK", "at": "2024-12-30T22:00:00"}
            }]
        }

        formatted_offer = format_flight_offer(shortest_flight)
        self.assertIn("Flight AA100 departing on December 25", formatted_offer["Departure"][0])
        self.assertIn("Flight AA101 departing on December 30", formatted_offer["Return"][0])

if __name__ == '__main__':
    unittest.main()
