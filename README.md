# Trip Planning API

This project provides a FastAPI-based backend that helps users plan trips. The API allows users to input a trip description, and it automatically generates a trip plan, including flight options, weather forecasts, and other essential details. The service utilizes OpenAI's ChatGPT to extract key information from user input, and integrates with flight and weather APIs for real-time data.

## Features

- **Trip Plan Generation**: Users can describe their trip (e.g., destination, dates), and the API will return a complete trip plan, including:
  - **Flights**: Flight options for the given trip.
  - **Weather**: Weather forecast for the destination.
  - **Description**: A short, human-readable description of the trip.
  
- **Date Validation**: Ensures that the trip's start and end dates are in the future and correctly formatted.

- **IATA Code Handling**: Automatically converts location names to IATA codes for destinations and origins.

## Getting Started

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn (for running the server)
- OpenAI API key (for ChatGPT interaction)
- Flight API key (for flight information)
- Weather API key (for weather forecast)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/trip-planning-api.git
  ```

2. Install the required dependencies:
  ```bash
    cd trip-planning-api
    pip install -r requirements.txt
  ```
3. Set up your API keys:

For ChatGPT, set your OpenAI API key in the openai_helper.py file.
For flight and weather information, set your API keys in the respective service files (flights.py, weather.py).
Running the Application
To start the API server, run:

  ```bash
    uvicorn main:app --reload
  ```
 This will start the server on http://127.0.0.1:8000, and you can start making requests to the /plan_trip endpoint.

## API Usage
### POST /plan_trip
#### Request Body:

```json

  {
    "user_input": "I want to travel from New York to Paris from January 10th to January 20th."
  }
  ```
Response:

```json
{
  "trip_plan": {
    "description": "Here is your trip plan to Paris from January 10th to January 20th.",
    "flights": {
      "flight_number": "AA123",
      "departure_time": "2024-01-10T08:00:00",
      "arrival_time": "2024-01-10T10:00:00",
      "price": "$500"
    },
    "weather_forecast": {
      "destination": "Paris",
      "forecast": "Partly cloudy, high of 10°C, low of 5°C"
    }
  }
}
```
## Error Handling
The API provides meaningful error messages for the following common issues:

400 Bad Request: If the input data is invalid, such as:

Invalid date format
Dates in the past
Missing or malformed keys in the ChatGPT response
Example:

```json
{
  "detail": "Invalid date format. Use 'YYYY-MM-DD'."
}
```

## Dependencies
FastAPI: The web framework used for building the API.
Uvicorn: ASGI server for running the FastAPI app.
requests: Library for making HTTP requests (currently not used but included for future expansion).
pydantic: Data validation and parsing.
openai: OpenAI API for interaction with ChatGPT.
License
This project is licensed under the MIT License - see the LICENSE file for details.





