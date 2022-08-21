from datetime import datetime, timedelta
from configparser import ConfigParser
import json
import os
from random import randrange

import requests
from pytz import timezone
from jinja2 import Environment, FileSystemLoader


def main():
    """Compile variables and pass into README"""
    (
        weather_dict,
        city_temperature,
        sunrise_time_unix,
        sunset_time_unix,
    ) = get_openweather_info()

    sunrise_time = str(convert_timestamp_to_MST(sunrise_time_unix).strftime("%H:%M %p"))

    # Convert from 24 hour to 12 hour clock
    sunset_time = convert_timestamp_to_MST(sunset_time_unix).strftime("%H:%M")
    sunset_time = datetime.strptime(sunset_time, "%H:%M").strftime("%I:%M %p")

    current_time_MST = datetime.now(timezone("US/Mountain")).strftime("%H:%M")
    current_time_MST = datetime.strptime(current_time_MST, "%H:%M").strftime("%I:%M %p")
    current_date = datetime.now(timezone("US/Mountain")).strftime("%Y-%m-%d")

    rand_quote, rand_author = random_quote()

    template_variables = {
        "state_name": "Utah",
        "current_datetime_MST": f"{current_date} {current_time_MST}",
        "current_time_MST": datetime.now(timezone("US/Mountain")).strftime("%I:%M %p"),
        "sun_rise": sunrise_time,
        "sun_set": sunset_time,
        "temperature": city_temperature,
        "weather_emoji": weather_icon(city_temperature),
        "rand_quote": rand_quote,
        "rand_author": rand_author
    }

    # Load template, pass in variables, write to README.md
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("main.html")
    output_from_parsed_template = template.render(template_variables)

    with open("README.md", "w+") as fh:
        fh.write(output_from_parsed_template)
    return


def _get_weather_api_key():
    """Fetch the API key from config file in local project.
    Otherwise, grab from GitHub secrets.
    Be sure to add "secrets.ini" to your .gitignore file!

    Expects a configuration file named "secrets.ini" with structure:

        [openweather]
        api_key=<YOUR-OPENWEATHER-API-KEY>
    """
    try:
        config = ConfigParser()
        config.read("secrets.ini")
        api_key = config["openweather"]["api_key"]
    except Exception:
        api_key = os.environ["openweather_api_key"]
    return api_key


def get_openweather_info():
    """Retrieve openweather data from API"""
    OPEN_WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?zip=84404,us&appid={_get_weather_api_key()}&units=standard"
    res = requests.get(OPEN_WEATHER_URL)
    weather_dict = json.loads(res.text)

    city_temperature = round(
        ((((weather_dict.get("main").get("temp")) - 273.15) * 1.8) + 32), 1
    )
    sunrise_time_unix = weather_dict.get("sys").get("sunrise")
    sunset_time_unix = weather_dict.get("sys").get("sunset")

    return weather_dict, city_temperature, sunrise_time_unix, sunset_time_unix


def weather_icon(temp):
    if temp >= 85:
        return '🥵🌞'
    elif temp <= 50:
        return '🏂 ❄️ ⛄'
    else:
        return '👌😄'


def convert_timestamp_to_MST(time_stamp):
    """Convert unix timestamp to UTC then MST"""
    UTC = datetime.utcfromtimestamp(time_stamp)
    return UTC + timedelta(hours=-6)


def random_quote():
    with open("quotes.json", "r") as data:
        quotes = json.load(data)
        last_key = int(sorted(quotes.keys())[-1])
        rand_key = str(randrange(1,last_key+1))
        rand_quote = quotes.get(rand_key)
        return rand_quote.get('Quote'), rand_quote.get('Author')

if __name__ == "__main__":
    main()
