from datetime import datetime
from configparser import ConfigParser
import json
import os

import requests
from pytz import timezone
from jinja2 import Environment, FileSystemLoader

def main():
  """Compile variables and pass into README
  """
  weather_dict, city_temperature, sunrise_time, sunset_time = get_openweather_info()
  print(weather_dict,sunrise_time)
  template_variables = {
    "state_name": 'Utah',
    "current_time_MST": datetime.now(timezone('US/Mountain')).strftime('%I:%M %p'),
    "sun_rise": str(sunrise_time.strftime('%I:%M %p')),
    "sun_set": str(sunset_time.strftime('%I:%M %p')),
    "temperature": city_temperature
  }

  env = Environment(loader=FileSystemLoader('templates'))
  template = env.get_template('main.html')
  output_from_parsed_template = template.render(template_variables)

  with open("readme.md", "w+") as fh:
    fh.write(output_from_parsed_template)


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
    except:
      api_key = os.environ['openweather_api_key']
    return api_key

def get_openweather_info():
  """Retrieve openweather data from API
  """
  OPEN_WEATHER_URL = f'http://api.openweathermap.org/data/2.5/weather?zip=84404,us&appid={_get_weather_api_key()}&units=standard'
  res = requests.get(OPEN_WEATHER_URL)
  weather_dict = json.loads(res.text)

  city_temperature = round(((((weather_dict.get('main').get('temp'))-273.15)*1.8)+32),1)
  sunrise_time = datetime.fromtimestamp(weather_dict.get('sys').get('sunrise'))
  sunset_time = datetime.fromtimestamp(weather_dict.get('sys').get('sunset'))
  
  return weather_dict, city_temperature, sunrise_time, sunset_time


if __name__ == '__main__':
  main()