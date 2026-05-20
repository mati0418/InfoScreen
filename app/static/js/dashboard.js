function formatDate(dateStr) {
    const days = [
        "Sonntag","Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag"
    ];
    const d = new Date(dateStr);
    return days[d.getDay()];
}


// -------------------- ICONS --------------------

function getWeatherIcon(code, time = "1200", sunrise = "600", sunset = "1800") {

    const isNightTime =
        Number(time) < Number(sunrise) ||
        Number(time) > Number(sunset);

    const dayNight = isNightTime ? "night-alt" : "day";

    const map = {
        113: isNightTime ? "wi-night-clear" : "wi-day-sunny",   // Sunny / Clear
        116: isNightTime ? "wi-night-alt-partly-cloudy" : "wi-day-sunny-overcast",   // Partly Cloudy
        119: `wi-${dayNight}-cloudy`,   // Cloudy
        122: "wi-cloudy",               // VeryCloudy / Overcast
        143: isNightTime ? "wi-night-fog" : "wi-day-fog",   // Fog / Mist

        176: `wi-${dayNight}-showers`,     // LightShowers / Patchy rain nearby
        179: `wi-${dayNight}-snow`,        // LightSleetShowers / Patchy snow nearby
        182: `wi-${dayNight}-sleet`,       // LightSleet / Patchy sleet nearby
        185: `wi-${dayNight}-rain-mix`,    // LightSleet / Patchy freezing drizzle nearby
        200: `wi-${dayNight}-lightning`,   // ThunderyShowers / Thundery outbreaks nearby
        227: `wi-${dayNight}-snow`,        // LightSnow / Blowing snow
        230: "wi-snow-wind",               // HeavySnow / Blizzard
        248: "wi-fog",   // Fog 
        260: "wi-fog",   // Fog / freezing fog

        263: `wi-${dayNight}-showers`,   // LightShowers / Patchy light drizzle
        266: `wi-${dayNight}-showers`,   // LightRain / Light drizzle
        281: `wi-${dayNight}-sleet`,     // LightSleet / Freezing drizzle
        284: "wi-sleet",                 // LightSleet / Heavy freezing drizzle

        293: `wi-${dayNight}-rain`,   // LightRain / Patchy light rain
        296: `wi-${dayNight}-rain`,   // LightRain / Light rain
        299: "wi-rain",               // HeavyShowers / Moderate rain at times
        302: "wi-rain",               // HeavyRain / Moderate rain
        305: "wi-rain-wind",          // HeavyShowers / Heavy rain at times
        308: "wi-rain-wind",          // HeavyRain / Heavy rain

        311: `wi-${dayNight}-rain-mix`,   // LightSleet / Light freezing rain
        314: "wi-rain-mix",               // LightSleet / Moderate or heavy freezing rain
        317: `wi-${dayNight}-sleet`,      // LightSleet / Light sleet
        320: "wi-sleet",                  // LightSnow / Moderate or heavy sleet

        323: `wi-${dayNight}-snow`,   // LightSnowShowers / Patchy light snow
        326: `wi-${dayNight}-snow`,   // LightSnowShowers / Light snow
        329: "wi-snow",               // HeavySnow / Patchy moderate snow
        332: "wi-snow",               // HeavySnow / Moderate snow
        335: `wi-${dayNight}-snow`,   // HeavySnowShowers / Patchy heavy snow
        338: "wi-snow-wind",          // HeavySnow / Heavy snow

        350: "wi-hail",                  // LightSleet / Ice pellets
        353: `wi-${dayNight}-showers`,   // LightShowers / Light rain shower
        356: "wi-showers",               // HeavyShowers / Moderate or heavy rain shower
        359: "wi-rain-wind",             // HeavyRain / Torrential rain shower

        362: `wi-${dayNight}-sleet`,   // LightSleetShowers / Light sleet showers
        365: "wi-sleet",               // LightSleetShowers / Moderate or heavy sleet showers
        368: `wi-${dayNight}-snow`,    // LightSnowShowers / Light snow showers
        371: "wi-snow",                // LightSnowShowers / Moderate or heavy snow showers

        374: `wi-${dayNight}-hail`,   // LightSleetShowers / Light showers of ice pellets
        377: "wi-hail",               // LightSleet / Moderate or heavy showers of ice pellets

        386: "wi-storm-showers",   // ThunderyShowers / Patchy light rain in area with thunder
        389: "wi-thunderstorm",    // ThunderyHeavyRain / Moderate or heavy rain in area with thunder
        392: "wi-storm-showers",   // ThunderySnowShowers / Patchy light snow in area with thunder
        395: "wi-thunderstorm",    // HeavySnowShowers / Moderate or heavy snow in area with thunder

        500: "wi-hot",
        501: "wi-snowflake-cold",
        502: "wi-strong-wind",
        503: "wi-day-windy",
        504: `wi-${dayNight}-cloudy-gusts`,
        505: "wi-cloudy-gusts",

        510: "wi-sunrise",
        511: "wi-sunset",
        512: "wi-stars",

        default: "wi-cloud"
    };

    return map[code] || map.default;
}


// -------------------- COLOR --------------------

function getIconColor(code) {
    code = parseInt(code);

    if ([113, 503, 510, 511, 512].includes(code))
        return "text-yellow-400";   // Sonne

    if ([116].includes(code))
        return "text-yellow-200";   // teilweise bewölkt

    if ([504].includes(code))
        return "text-gray-300";   // windig

    if ([119,122,502,505].includes(code))
        return "text-gray-400";   // bewölkt

    if ([143,248,260].includes(code))
        return "text-gray-500";   // Nebel

    if ([176,182,185,263,266,281,284,293,296,
         299,302,305,308,356,359,311,314,317,
         320,350,353,362,365,374,377].includes(code))
        return "text-blue-400";   // Regen oder Sleet

    if ([179,227,230,323,326,329,332,335,338,
         368,371,395,501].includes(code))
        return "text-white";   // Schnee

    if ([200,386,389,392,500].includes(code))
        return "text-orange-400";   // Gewitter

    return "text-gray-300";
}


// -------------------- TIME --------------------

function updateTime() {
    const now = new Date();

    document.getElementById("current-time").innerHTML =
        `${now.getHours().toString().padStart(2,"0")}:` +
        `${now.getMinutes().toString().padStart(2,"0")}`;
}


// -------------------- WEATHER LOAD --------------------

async function loadWeather() {
    const res = await fetch("/weather");
    const data = await res.json();

    // CURRENT
    document.getElementById("current").innerHTML = `
        <div class="flex w-full items-center gap-6 mb-6">

            <i class="wi ${data.current.text} text-8xl"></i>

            <div class="text-6xl">${data.current.temp}°C</div>
        </div>

        <div class="text-4xl opacity-80">
            ${data.current.desc}
        </div>
    `;


    // FORECAST
    let forecastHtml = "";

    data.forecast.forEach(day => {

        let hourlyHtml = "";

        day.hourly.forEach(hour => {
            hourlyHtml += `
                <div class="flex gap-8 bg-slate-700 p-4 rounded-lg w-full items-center shadow">
                    <div class="font-bold text-2xl w-1/6 text-right">
                        ${hour.time.padStart(3,"0").slice(0,-2)}:00
                    </div>

                    <i class="wi ${hour.text} text-4xl w-1/6"></i>

                    <div class="text-2xl opacity-80 w-3/6">
                        ${hour.desc}
                    </div>

                    <div class="text-2xl text-center w-1/6">
                        ${hour.temp}°
                    </div>
                </div>
            `;
        });

        forecastHtml += `
            <div class="bg-slate-800 grid grid-cols-2 p-6 rounded-2xl w-1/3 content-start shadow-lg">

                <div class="font-bold mb-2 text-4xl text-center col-span-2 h-12">
                    ${formatDate(day.date)}
                </div>

                <i class="wi ${day.text} h-32 text-8xl text-center row-span-2 "></i>

                <div class="text-2xl h-16 opacity-80">
                    ${day.desc}
                </div>

                <div class="text-2xl h-16">
                    ${day.max}° / ${day.min}°
                </div>

                <div class="col-span-full">
                    ${hourlyHtml}
                </div>
            </div>
        `;
    });

    document.getElementById("forecast").innerHTML = forecastHtml;
}


// -------------------- INIT --------------------

loadWeather();
updateTime();

setInterval(loadWeather, 300000);
setInterval(updateTime, 60000);