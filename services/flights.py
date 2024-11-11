import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

AMADEUS_CLIENT_ID = os.environ["AMADEUS_CLIENT_ID"]
AMADEUS_CLIENT_SECRET = os.environ["AMADEUS_CLIENT_SECRET"]

# Helper function to get IATA code from city name
def get_iata_code(city_name):
    # Authenticate with Amadeus API
    response = requests.post(
        "https://test.api.amadeus.com/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": AMADEUS_CLIENT_ID,
            "client_secret": AMADEUS_CLIENT_SECRET
        }
    )
    access_token = response.json().get("access_token")
    
    location_response = requests.get(
        "https://test.api.amadeus.com/v1/reference-data/locations",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "keyword": city_name,
            "subType": "CITY"
        }
    )
    locations = location_response.json().get("data", [])
    if locations:
        return locations[0]["iataCode"]
    else:
        error = location_response.json()[errors][0]["detail"]
        raise HTTPException(status_code=404, detail=error)


# Helper function to get flights
def get_flights(origin_iata, destination_iata, departure_date, return_date):
    # Convert city names to IATA codes


    # Authenticate with Amadeus API
    response = requests.post(
        "https://test.api.amadeus.com/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": AMADEUS_CLIENT_ID,
            "client_secret": AMADEUS_CLIENT_SECRET
        }
    )
    access_token = response.json().get("access_token")
    
    flight_response = requests.get(
        "https://test.api.amadeus.com/v2/shopping/flight-offers",
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "originLocationCode": origin_iata,
            "destinationLocationCode": destination_iata,
            "departureDate": departure_date,
            "returnDate": return_date,
            "adults": 1
        }
    )

    flights = flight_response.json().get("data", [])
    return flights



def format_flight_offer(flight_offer):
    # Helper function to convert date format
    def format_date(date_str):
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        return date_obj.strftime("%B %d").replace(" 0", " ").replace(
            "1 ", "1st ").replace("2 ", "2nd ").replace("3 ", "3rd ").replace("21 ", "21st ").replace("22 ", "22nd ").replace("23 ", "23rd ")
    
    # Format each flight segment into the desired structure
    flight_dict = {}
    itineraries = flight_offer.get("itineraries", [])
    
    for i, itinerary in enumerate(itineraries):
        direction = "Departure" if i == 0 else "Return"
        segments = itinerary["segments"]
        
        # List to store each segment formatted as "Flight XYZ123 departing on November 1st from Paris to Rome"
        flights = []
        for segment in segments:
            flight_num = f"{segment['carrierCode']}{segment['number']}"
            departure_airport = segment["departure"]["iataCode"]
            arrival_airport = segment["arrival"]["iataCode"]
            departure_date = format_date(segment["departure"]["at"])
            
            flights.append(
                f"Flight {flight_num} departing on {departure_date} from {departure_airport} to {arrival_airport}"
            )
        
        flight_dict[direction] = flights

    return flight_dict