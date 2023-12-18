from datetime import datetime

from pytz import timezone
from jinja2 import Environment, FileSystemLoader

from infrastructure import weather, quotes

def main():
    """Compile variables and pass into README"""
    (
        weather_dict,
        city_temperature,
        sunrise_time_unix,
        sunset_time_unix,
    ) = weather.get_openweather_info()

    timestamp = weather.convert_timestamp_to_MST(sunrise_time_unix)
    formatted_time = timestamp.strftime("%H:%M %p")
    sunrise_time = str(formatted_time)

    # Convert from 24 hour to 12 hour clock
    sunset_time = weather.convert_timestamp_to_MST(sunset_time_unix).strftime("%H:%M")
    sunset_time = datetime.strptime(sunset_time, "%H:%M").strftime("%I:%M %p")

    current_time_MST = datetime.now(timezone("US/Mountain")).strftime("%H:%M")
    current_time_MST = datetime.strptime(current_time_MST, "%H:%M").strftime("%I:%M %p")
    current_date = datetime.now(timezone("US/Mountain")).strftime("%Y-%m-%d")

    # Grab a random quote
    rand_quote, rand_author = quotes.random_quote()

    # Grab current pollution summary data
    aqi, pm10 = weather.get_openweather_air_quality()

    # Update PM10.json, render plot, and grab summary data
    weather.update_PM10_json(f"{current_date} {current_time_MST}", pm10, aqi)
    weather.render_PM10_plots()
    pm10_data_point_count, count_exceeding_EPA, days_of_AQI_data = \
        weather.summarize_PM10_json()
    days_exceeding_EPA_percentage = round((count_exceeding_EPA / pm10_data_point_count)*100, 1)

    template_variables = {
        "state_name": "Utah",
        "current_datetime_MST": f"{current_date} {current_time_MST}",
        "current_time_MST": datetime.now(timezone("US/Mountain")).strftime("%I:%M %p"),
        "sun_rise": sunrise_time,
        "sun_set": sunset_time,
        "temperature": city_temperature,
        "weather_emoji": weather.weather_icon(city_temperature),
        "rand_quote": rand_quote,
        "rand_author": rand_author,
        "AQI": aqi,
        "PM10": pm10,
        "days_of_AQI_data": days_of_AQI_data,
        "count_exceeding_EPA": count_exceeding_EPA,
        "pm10_data_point_count": pm10_data_point_count,
        "days_exceeding_EPA_percentage": str(days_exceeding_EPA_percentage) + "%",
        "PM10_plots_HTML": weather.generate_html_for_png_files()
    }

    # Load template, pass in variables, write to README.md
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("main.html")
    output_from_parsed_template = template.render(template_variables)

    with open("README.md", "w+") as fh:
        fh.write(output_from_parsed_template)

    return

if __name__ == "__main__":
    main()
