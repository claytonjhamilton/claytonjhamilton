// index.js
const Mustache = require('mustache');
const fetch = require("node-fetch");
const fs = require('fs');
const MUSTACHE_MAIN_DIR = './main.mustache';

let DATA = {
  name: 'Clayton Hamilton, PharmD',
  date: new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    timeZoneName: 'short',
    timeZone: 'America/Denver',
  }),
  time: new Date().toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: 'numeric',
    timeZoneName: 'short',
    timeZone: 'America/Denver',
  }),
};

async function setWeatherInformation() {
  await fetch(
   `http://api.openweathermap.org/data/2.5/weather?zip=84105,us&appid=${process.env.OPEN_WEATHER_MAP_KEY}&units=standard`
  )
    .then(r => r.json())
    .then(r => {
      // Convert Kelvin to Fahrenheit
      DATA.city_temperature = (((Math.round(r.main.temp)-273.15)*1.8)+32).toFixed(1);
      // Weather label      
      if (r.weather[0].main == `Clear`) {
        DATA.weather_description = `the sky is clear which means I'll either be running or rock climbing at some point today`;
      } else if (r.weather[0].main == `Thunderstorm`)  {
        DATA.weather_description = `it's currently storming so I may stay indoors today`;
      } else if (r.weather[0].main == `Drizzle`) {
        DATA.weather_description = `it's lightly raining so I may go for a run`;
      } else if (r.weather[0].main == `Rain`) {
        DATA.weather_description = `it's currently raining so I may stay indoors today`;
      } else if (r.weather[0].main == `Snow`) {
        DATA.weather_description = `snowflakes are falling so I'm considering snowboarding this weekend`;
      } else if (r.weather[0].main == `Clouds`) {
        DATA.weather_description = `it's a cloudy day so I'll likely go for a run`;
      } else {
        DATA.weather_description = `the atmosphere is hazy outside`;
      }
      DATA.city_name = r.name;
      DATA.city_weather_icon = r.weather[0].icon;
      DATA.sun_rise = new Date(r.sys.sunrise * 1000).toLocaleString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'America/Denver',
      });
      DATA.sun_set = new Date(r.sys.sunset * 1000).toLocaleString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'America/Denver',
      });
    });
}

async function RandomStarWarsQuote() {
  await fetch(
    `http://swquotesapi.digitaljedi.dk/api/SWQuote/RandomStarWarsQuote`
    )
    .then(r => r.json())
    .then(r => {
      DATA.starWarsQuote = r.starWarsQuote;
    });
}

function generateReadMe() {
  fs.readFile(MUSTACHE_MAIN_DIR, (err, data) =>  {
    if (err) throw err;
    const output = Mustache.render(data.toString(), DATA);
    fs.writeFileSync('README.md', output);
  });
}

async function action() {
  // Fetch Weather
  await setWeatherInformation();

  // Fetch random Star Wars quote
  await RandomStarWarsQuote();

  // Generate README
  await generateReadMe();
};

action();