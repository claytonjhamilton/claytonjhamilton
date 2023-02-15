from configparser import ConfigParser
from datetime import datetime, timedelta
import json
import os

import matplotlib.pyplot as plt
import pandas as pd
import requests
from scipy.stats import linregress


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
    WEATHER_API_KEY = _get_weather_api_key()
    OPEN_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?"
    OPEN_WEATHER_URL += f"zip=84404,us&appid={WEATHER_API_KEY}&units=standard"
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


def get_openweather_air_quality():
    base_url = "http://api.openweathermap.org/data/2.5/air_pollution?"
    api_key = f"appid={_get_weather_api_key()}"
    AIR_QUALITY_URL = f"{base_url}lat=41.2230&lon=111.9738&{api_key}"

    res = requests.get(AIR_QUALITY_URL)
    air_quality_dict = json.loads(res.text)
    pm10 = air_quality_dict.get("list")[0].get("components").get("pm10")
    aqi = air_quality_dict.get("list")[0].get("main").get("aqi")
    if aqi == 1:
        return "good" , pm10
    elif aqi == 2:
        return "fair" , pm10
    elif aqi == 3:
        return "moderate" , pm10
    elif aqi == 4:
        return "poor" , pm10
    elif aqi == 5:
        return "very poor" , pm10

def update_PM10_json(timestamp, PM10, aqi):
    with open("data/PM10.json") as doc:
        docObj = json.load(doc)
        docObj.append(
            {
            "DateTime": timestamp,
            "PM10": PM10,
            "AQI": aqi
            }
        )
    with open("data/PM10.json", 'w') as json_file:
        json.dump(docObj, json_file, 
                  indent=4,  
                  separators=(',',': '))
    return

def summarize_PM10_json():
    with open("data/PM10.json") as doc:
        df = pd.read_json(doc)
    df['Date_'] = pd.to_datetime(df['DateTime'])
    date_only = df['Date_'].dt.date
    count_exceeding_EPA = len(df[df['PM10'] >= 50])
    return len(df), count_exceeding_EPA, len(date_only.unique())

def next_two_weeks():
    # Get tomorrow's date
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    # Get the date 2 weeks from today
    two_weeks_from_now = tomorrow + timedelta(days=14)

    # Create a range of dates from tomorrow to 2 weeks
    two_week_date_range = range((two_weeks_from_now - tomorrow).days)
    return [tomorrow + timedelta(days=x) for x in two_week_date_range]


def render_PM10_plot():
    df = pd.read_json('data/PM10.json')
    df['DateTimeNumeric'] = pd.to_numeric(df.DateTime)
    df['DateTime'] = pd.to_datetime(df.DateTime) 

    # Simple linear regression
    x = df['DateTimeNumeric']
    y = df['PM10']
    beta_one, beta_zero, r_val, p_val_beta_1, stderr_beta_1 = linregress(x=x, y=y)

    # Create figure and plot space
    fig, ax = plt.subplots(figsize=(10, 6))
    
    plt.scatter(x=df['DateTime'],
                y=df['PM10'],
                s=None,
                c='blue')

    # Add linear regression line
    x = df['DateTime'].values
    y = beta_zero + beta_one * pd.to_numeric(x)

    plt.plot(x
            ,y
            ,color='red'
            ,label='OLS Linear regression',
            linewidth=4)

    plt.axhline(y=50, 
                color='green', 
                linestyle='-',
                label="US EPA recommended level",
                linewidth=4)
            
    plt.legend()
    # Set title and labels for axes
    ax.set(xlabel="Date",
           ylabel="PM10",
           title="PM10 trends in Ogden, UT")
    plt.savefig('PM10_plot.png')
    return

