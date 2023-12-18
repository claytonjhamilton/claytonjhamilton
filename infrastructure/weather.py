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

def render_PM10_plots():
    """Render a plot for each year of captured data
    """
    df = pd.read_json('data/PM10.json')
    df['DateTimeNumeric'] = pd.to_numeric(df['DateTime'])
    df['DateTime'] = pd.to_datetime(df['DateTime']) 

    # Group data by year
    grouped_by_year = df.groupby(df['DateTime'].dt.year)

    # Iterate over each group (year) and create a separate plot
    for year, group in grouped_by_year:
        # Simple linear regression
        x = group['DateTimeNumeric']
        y = group['PM10']
        beta_one, beta_zero, _, _, _ = linregress(x=x, y=y)

        # Create figure and plot space
        fig, ax = plt.subplots(figsize=(10, 6))

        plt.scatter(x=group['DateTime'],
                    y=group['PM10'],
                    s=None,
                    c='blue')

        # Add linear regression line
        x_values = group['DateTime'].values
        y_values = beta_zero + beta_one * pd.to_numeric(x_values)

        plt.plot(x_values, y_values, color='red', label='OLS Linear regression', linewidth=4)

        plt.axhline(y=50, color='green', linestyle='-', label="US EPA recommended level", linewidth=4)
            
        plt.legend()
        
        # Set title and labels for axes
        ax.set(xlabel="Date",
               ylabel="PM10",
               title=f"PM10 trends in Ogden, UT - Year {year}")
        
        # Save each plot with a unique filename
        plt.savefig(f'PM10_plot_{year}.png')
        
        # Close the current plot to avoid overlapping when creating the next one
        plt.close()

    return

def generate_html_for_png_files(folder_path='./'):
    # Get a list of all files in the folder
    all_files = os.listdir(folder_path)

    # Filter files that end with ".png" and start with "PM10_"
    png_files = [file for file in all_files if file.endswith('.png') and file.startswith('PM10_')]

    # Sort the list of PNG files
    png_files.sort(reverse=True)

    # Generate HTML output
    html_output = ''
    for png_file in png_files:
        html_output += f'<img src="{png_file}" width="600" height="400">\n'

    return html_output
