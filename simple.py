from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from services.openai_helper import get_chatgpt_response

# Initialize the FastAPI application
app = FastAPI()

# Define the request body model for trip planning
class TripRequest(BaseModel):
    user_input: str

# Main route to handle trip requests
@app.post("/plan_trip")
async def plan_trip(trip_request: TripRequest):
    # Extract the user input from the request
    user_input = trip_request.user_input

    # Construct prompt for ChatGPT to generate trip details
    prompt = f"""
    In the following CONTEXT, you will receive a travel description.
    Extract the location and dates, convert the location to IATA codes, and retrieve flight and weather details for the trip.

    Note: Only search the web for flights and weather; no code is needed in the response.
    Return the response in JSON format, following the example exactly, so it can be parsed by json.loads.

    Example Output:
    {{
        "trip_plan": {{
            "description": "Here is your trip plan to Tel-Aviv from November 12th to November 15th.",
            "flights": {{
                "Departure": [
                    "Flight AF962 departing on November 12 from CDG to TLV"
                ],
                "Return": [
                    "Flight AF963 departing on November 15 from TLV to CDG"
                ]
            }},
            "weather_forecast": [
                "November 12th: clear sky, 20.69 °C",
                "November 13th: clear sky, 20.64 °C",
                "November 14th: broken clouds, 20.36 °C",
                "November 15th: clear sky, 18.66 °C"
            ]
        }}
    }}

    CONTEXT:
    {user_input}
    """
    # Get response from ChatGPT based on the prompt
    return get_chatgpt_response(prompt)

# Run the FastAPI application if the script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
