from services.openai_helper import get_chatgpt_response
from services.flights import (
    get_flights,
    format_flight_offer,
    get_iata_code,
    find_flight_with_smallest_segments
)
from services.weather import get_weather
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import time

# Initialize FastAPI application
app = FastAPI()

# Define request body model for trip planning
class TripRequest(BaseModel):
    user_input: str

# Main endpoint for trip planning
@app.post("/plan_trip")
async def plan_trip(trip_request: TripRequest):
    user_input = trip_request.user_input

    # Get the current year and month for handling missing date information
    current_year = datetime.now().year
    current_month = datetime.now().month

    # Prepare the prompt for ChatGPT to parse trip information from user input
    prompt = f"""
    Given the trip context, perform the following:
    1. Extract destination, origin, start date, and end date.
    2. Convert dates to YYYY-MM-DD. If year is missing, use '{current_year}'; if month is missing, use '{current_month}'.
    3. Determine if origin and destination are valid cities (boolean).
    4. Attempt to convert them to IATA codes. If not possible, return None.
    5. Provide the nearest city with an airport as 'nearest'.
    6. Provide a summary in this format: 'Here is your trip plan to Rome from November 1st to November 10th.'

    CONTEXT:
    {user_input}

    Return response in the following JSON format:
    {{
        "destination": {{
            "name": str,
            "city": bool,
            "code": str,
            "nearest": {{
                "name": str,
                "code": str
            }}
        }},
        "origin": {{
            "name": str,
            "city": bool,
            "code": str,
            "nearest": {{
                "name": str,
                "code": str
            }}
        }},
        "start_date": str,
        "end_date": str,
        "description": str
    }}
    """

    # Retry mechanism for handling ChatGPT request errors
    retries = 3
    for attempt in range(retries):
        try:
            chatgpt_response = get_chatgpt_response(prompt)
            break
        except Exception:
            print("Retrying in 5 seconds...")
            time.sleep(5)

    # Validate response: Check if origin and destination are valid cities
    if not chatgpt_response.get("destination", {}).get("city"):
        raise HTTPException(status_code=400, detail="Destination is not a city.")
    if not chatgpt_response.get("origin", {}).get("city"):
        raise HTTPException(status_code=400, detail="Origin is not a city.")

    try:
        # Extract necessary data from ChatGPT response
        origin_code = chatgpt_response["origin"]["nearest"]["code"]
        destination_code = chatgpt_response["destination"]["nearest"]["code"]
        description = chatgpt_response["description"]
        destination = chatgpt_response["destination"]["nearest"]["name"]
        origin = chatgpt_response["origin"]["nearest"]["name"]
        start_date = chatgpt_response["start_date"]
        end_date = chatgpt_response["end_date"]
    except (SyntaxError, KeyError):
        raise HTTPException(status_code=400, detail="Failed to parse ChatGPT response.")

    # Validate dates: Convert to datetime objects and ensure they are in the future
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD'.")

    current_date = datetime.now()
    if start_date_obj < current_date or end_date_obj < current_date:
        raise HTTPException(status_code=400, detail="Travel dates must be in the future.")
    if start_date_obj > end_date_obj:
        raise HTTPException(status_code=400, detail="Start date must be before end date.")

    # Retrieve IATA codes if not provided
    if origin_code is None:
        origin_code = get_iata_code(origin)
    if destination_code is None:
        destination_code = get_iata_code(destination)

    # Get flight details based on origin, destination, and travel dates
    flights = get_flights(origin_code, destination_code, start_date, end_date)
    if not flights:
        raise HTTPException(status_code=400, detail="No flights found.")

    # Get weather forecast for destination during travel period
    weather_forecast = get_weather(destination, start_date_obj, end_date_obj)

    # Find the shortest flight and format the trip plan response
    shortest_flight = find_flight_with_smallest_segments(flights)
    trip_plan = {
        "description": description,
        "flights": format_flight_offer(shortest_flight),
        "weather_forecast": weather_forecast
    }

    return {"trip_plan": trip_plan}

# Run the FastAPI application if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
