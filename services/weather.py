import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict, Counter

# Load environment variables from .env file
load_dotenv()

# Initialize OpenWeather API key
OPENWEATHER_API_KEY = os.environ['OPENWEATHER_API_KEY']

# Fetch weather forecast for a given destination between start and end dates
def get_weather(destination, start_date, end_date):
    # Prepare the OpenWeather API URL
    openweather_api_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?q={destination}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    # Request weather data from OpenWeather API
    response = requests.get(openweather_api_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch weather data for {destination}")

    days = response.json().get("list", [])
    weather_forecast = []

    # Filter weather data within the specified date range
    for day in days:
        date_object = datetime.strptime(day["dt_txt"], "%Y-%m-%d %H:%M:%S")
        if start_date <= date_object <= end_date:
            # Format date as "Month Day" with appropriate suffix
            formatted_date = date_object.strftime("%B %d").replace(" 0", " ")
            suffix = 'th' if 4 <= date_object.day <= 20 or 24 <= date_object.day <= 30 else ['st', 'nd', 'rd'][date_object.day % 10 - 1]
            formatted_date += suffix

            # Append weather details to forecast list
            weather_forecast.append((formatted_date, day["weather"][0]["description"], day["main"]["temp"]))

    # Aggregate daily weather data
    daily_forecasts = defaultdict(list)
    for date, condition, temperature in weather_forecast:
        daily_forecasts[date].append((condition, temperature))

    # Summarize weather for each day
    daily_summary = []
    for date, entries in daily_forecasts.items():
        # Determine the most frequent weather condition
        conditions = [condition for condition, temp in entries]
        most_common_condition = Counter(conditions).most_common(1)[0][0]

        # Calculate the average temperature for the day
        avg_temp = sum(temp for _, temp in entries) / len(entries)

        # Format daily summary
        summary = f"{date}: {most_common_condition}, {avg_temp:.2f} °C"
        daily_summary.append(summary)

    return daily_summary
