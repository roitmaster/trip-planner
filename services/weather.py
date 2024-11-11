import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict, Counter
load_dotenv()

OPENWEATHER_API_KEY = os.environ['OPENWEATHER_API_KEY']
def get_weather(destination, start_date, end_date):
    openweather_api_url = f"https://api.openweathermap.org/data/2.5/forecast?q=tel aviv&appid=b242d710c8afed1b54f2faba7cf171a2&units=metric".lower()
    response = requests.get(openweather_api_url, headers={}, data={})
    days = response.json().get("list", [])
    weather_forecast = []
    for day in days:
        date_object = datetime.strptime(day["dt_txt"], "%Y-%m-%d %H:%M:%S")
        if date_object >= start_date and date_object <= end_date:


            formatted_date = date_object.strftime("%B %dth").replace(" 0", " ")

            # Handle the "th" suffix for the day
            if 4 <= date_object.day <= 20 or 24 <= date_object.day <= 30:
                suffix = 'th'
            else:
                suffix = ['st', 'nd', 'rd'][date_object.day % 10 - 1]

            # Add suffix to the day
            formatted_date = formatted_date.replace("th", suffix) if "th" in formatted_date else formatted_date

            weather_forecast.append((formatted_date, day["weather"][0]["description"], day["main"]["temp"]))

    daily_forecasts = defaultdict(list)

    for entry in weather_forecast:
        date, condition, temperature = entry
        daily_forecasts[date].append((condition, temperature))

    # Summarize each day
    daily_summary = []
    for date, entries in daily_forecasts.items():
        # Get the most frequent weather condition
        conditions = [condition for condition, temp in entries]
        most_common_condition = Counter(conditions).most_common(1)[0][0]
        # Get the highest temperature of the day
        avg_temp = sum(temp for condition, temp in entries)/(len(entries))
        # Format the summary
        summary = f"{date}: {most_common_condition}, {avg_temp:.2f} °C"
        daily_summary.append(summary)

    return daily_summary
