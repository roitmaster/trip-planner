from services.openai_helper import get_chatgpt_response
from services.flights import get_flights, format_flight_offer, get_iata_code
from services.weather import get_weather
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime

# Initialize the FastAPI application
app = FastAPI()

# Define the request body model using Pydantic
class TripRequest(BaseModel):
    user_input: str

# Main route to handle trip planning requests
@app.post("/plan_trip")
async def plan_trip(trip_request: TripRequest):
    # Extract user input from the request body
    user_input = trip_request.user_input

    # Get the current year and month for date handling
    year = datetime.now().year
    month = datetime.now().month

    # Construct a prompt to pass to the ChatGPT model to extract trip information
    prompt = f"""
    A given context describe a trip plan. Extract from the context the destination, origin, start date, and end date in YYYY-MM-DD format,
if the year is not given use '{year}' and if month use '{month}'. convert the destination and origin to IATA code if possible as destinationCode
and originCode if not return as None. also provide short description in the like in a format: `Here is your trip plan to Rome from November 1st to November 10th.`
\n CONTEXT:'{user_input}'. Return the response in JSON format with keys: destination, origin, destinationCode, originCode, start_date, end_date, description.
"""
    
    # Call the ChatGPT API to interpret the user input
    chatgpt_response = get_chatgpt_response(prompt)

    try:
        # Extract the relevant data from the ChatGPT response
        originCode = chatgpt_response["originCode"]
        destinationCode = chatgpt_response["destinationCode"]
        description = chatgpt_response["description"]
        destination = chatgpt_response["destination"]
        origin = chatgpt_response["origin"]
        start_date = chatgpt_response["start_date"]
        end_date = chatgpt_response["end_date"]
    except (SyntaxError, KeyError):
        # Raise an error if the response is invalid or parsing fails
        raise HTTPException(status_code=400, detail="Failed to parse ChatGPT response.")

    # Convert start and end dates from strings to datetime objects for validation
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        # Raise an error if the date format is incorrect
        raise HTTPException(status_code=400, detail="Invalid date format. Use 'YYYY-MM-DD'.")

    # Check if the travel dates are in the future
    current_date = datetime.now()
    if start_date_obj < current_date or end_date_obj < current_date:
        # Raise an error if any date is in the past
        raise HTTPException(status_code=400, detail="Travel dates must be in the future.")
    if start_date_obj > end_date_obj:
        # Raise an error if the start date is after the end date
        raise HTTPException(status_code=400, detail="Start date must be before end date.")

    # Get IATA codes if they were not provided in the ChatGPT response
    if originCode is None:
        originCode = get_iata_code(origin)
    if destinationCode is None:
        destinationCode = get_iata_code(destination)

    # Fetch flight options based on the origin, destination, and dates
    flights = get_flights(originCode, destinationCode, start_date, end_date)
    
    # Fetch the weather forecast for the destination during the specified dates
    weather_forecast = get_weather(destination, start_date_obj, end_date_obj)

    # Structure the trip plan into a JSON format for the response
    trip_plan = {
        "description": description,  # Short description of the trip
        "flights": format_flight_offer(flights[0]),  # Flight offer details
        "weather_forecast": weather_forecast  # Weather forecast details
    }

    # Return the structured trip plan as a JSON response
    return {"trip_plan": trip_plan}

# Run the FastAPI application if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
