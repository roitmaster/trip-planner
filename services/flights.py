import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI, HTTPException
from amadeus import Location, Client

# Load environment variables from .env file
load_dotenv()

# Initialize Amadeus API credentials
AMADEUS_CLIENT_ID = os.environ["AMADEUS_CLIENT_ID"]
AMADEUS_CLIENT_SECRET = os.environ["AMADEUS_CLIENT_SECRET"]

# Initialize Amadeus API client
def get_amadeus_client():
    return Client(client_id=AMADEUS_CLIENT_ID, client_secret=AMADEUS_CLIENT_SECRET)

# Helper function to fetch location data from Amadeus API
def get_location(keyword, subType=Location.ANY):
    amadeus = get_amadeus_client()
    return amadeus.reference_data.locations.get(keyword=keyword, subType=subType)

# Helper function to fetch cities data from Amadeus API
def get_cities(keyword):
    amadeus = get_amadeus_client()
    return amadeus.reference_data.locations.cities.get(keyword=keyword)

# Get IATA code for a city name
def get_iata_code(city_name):
    location_response = get_location(city_name, subType=Location.ANY)
    if location_response.status_code == 200:
        locations = location_response.result.get("data", [])
        if locations:
            return locations[0]["iataCode"]
    raise HTTPException(status_code=404, detail=f"IATA code for {city_name} not found")

# Get city and country from IATA code
def get_city_country_from_iata(iata_code):
    try:
        location_response = get_location(iata_code, subType=Location.ANY)
        if location_response.status_code == 200:
            data = location_response.result.get('data', [])
            if data:
                city = data[0]['address']['cityName']
                country = data[0]['address']['countryCode']
                return city, country
            else:
                location_response = get_cities(iata_code)
                data = location_response.result.get('data', [])
                if data:
                    city = data[0]['address']['cityName']
                    country = data[0]['address']['countryCode']
                    return city, country
        return None, None

    except Exception:
        return None, None

# Get flight offers between origin and destination
def get_flights(origin_iata, destination_iata, departure_date, return_date):
    amadeus = get_amadeus_client()
    flight_response = amadeus.shopping.flight_offers_search.get(
        originLocationCode=origin_iata,
        destinationLocationCode=destination_iata,
        departureDate=departure_date,
        returnDate=return_date,
        adults=1
    )
    return flight_response.result.get("data", [])

# Find the flight with the fewest segments for each direction
def find_flight_with_smallest_segments(flight_offers):
    departure_flight = None
    return_flight = None

    for flight_offer in flight_offers:
        itineraries = flight_offer.get("itineraries", [])
        for i, itinerary in enumerate(itineraries):
            direction = "Departure" if i == 0 else "Return"
            segments = itinerary["segments"]

            if direction == 'Departure':
                if departure_flight is None or len(segments) < len(departure_flight):
                    departure_flight = segments
            elif direction == 'Return':
                if return_flight is None or len(segments) < len(return_flight):
                    return_flight = segments
    return {"Departure": departure_flight, "Return": return_flight}

# Format flight offer details into a user-friendly structure
def format_flight_offer(shortest_flight):
    # Helper function to format date into a readable string
    def format_date(date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return date_obj.strftime("%B %d").replace(" 0", " ").replace(
            "1 ", "1st ").replace("2 ", "2nd ").replace("3 ", "3rd ").replace("21 ", "21st ").replace("22 ", "22nd ").replace("23 ", "23rd ")

    flight_dict = {}
    for direction, segments in shortest_flight.items():
        flights = []
        for segment in segments:
            flight_num = f"{segment['carrierCode']}{segment['number']}"
            departure_airport_code = segment["departure"]["iataCode"]
            arrival_airport_code = segment["arrival"]["iataCode"]
            departure_city, departure_country = get_city_country_from_iata(departure_airport_code)
            arrival_city, arrival_country = get_city_country_from_iata(arrival_airport_code)
            departure_date = format_date(segment["departure"]["at"])

            # Format flight path description
            if departure_city and arrival_city:
                flight_path = f"from {departure_city}, {departure_country} to {arrival_city}, {arrival_country} ({departure_airport_code} -> {arrival_airport_code})"
            else:
                flight_path = f"from {departure_airport_code} to {arrival_airport_code}"

            flights.append(
                f"Flight {flight_num} departing on {departure_date} {flight_path}"
            )
        
        flight_dict[direction] = flights

    return flight_dict
