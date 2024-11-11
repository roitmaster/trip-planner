import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from services.openai_helper import get_chatgpt_response

# Initialize the FastAPI application
app = FastAPI()


# Define the request body model
class TripRequest(BaseModel):
    user_input: str


# Main route to handle trip requests
@app.post("/plan_trip")
async def plan_trip(trip_request: TripRequest):
    user_input = trip_request.user_input


    prompt = f"""in the following CONETEX you will get a travel description extract the location and the dates convert the location to IATA and find me a flight and the weather in my trip days

i don't need the code just search the web and return me the flights details

Return the response in JSON format as in the output example, without adding additional information in the beginning or and the end so the respond will be parsed by json.loads function
output example:

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

CONTEXT :
{user_input}
"""
    return get_chatgpt_response(prompt)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)