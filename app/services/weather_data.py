import requests
from datetime import datetime
from app.Models.weather_data_model import WeatherDataDay, WeatherDataHour

# WI-Wethercodes zu Listen:
SHOWERS = ["176", "263", "266", "353", "356"]
SNOW = ["179", "227", "230", "329", "332", "335", "338", "368", "371"]
SLEET = ["182", "281", "284", "320", "362", "365"]
RAIN_MIX = ["185", "311", "311", "314"]
LIGHTNING = ["200", "386", "389", "392", "395"]
FOG = ["143", "248", "260", "143"]
RAIN = ["293", "296", "299", "302", "305", "308", "359"]
HAIL = ["350", "374", "377"]
CLEAR = ["113"]
PARTLY_CLOUDY = ["116"]
VERY_CLOUDY = ["119"]
CLOUDY = ["122"]

def get_Moonphase(illumination, moon_phase):
    moon_illumination = int(illumination)
    
    waxing = True if "Waxing" in moon_phase else False
    text = "wi-moon-"
    
    if moon_illumination <= 1:
        text += "new"
    elif moon_illumination <= 8:
        text += "waxing-crescent-1" if waxing else "waning-crescent-6"
    elif moon_illumination <= 15:
        text += "waxing-crescent-2" if waxing else "waning-crescent-5"
    elif moon_illumination <= 22:
        text += "waxing-crescent-3" if waxing else "waning-crescent-4"
    elif moon_illumination <= 29:
        text += "waxing-crescent-4" if waxing else "waning-crescent-3"
    elif moon_illumination <= 36:
        text += "waxing-crescent-5" if waxing else "waning-crescent-2"
    elif moon_illumination <= 44:
        text += "waxing-crescent-6" if waxing else "waning-crescent-1"
    elif moon_illumination <= 55:
        text += "first-quarter" if waxing else "third-quarter"
    elif moon_illumination <= 62:
        text += "waxing-gibbous-1" if waxing else "waning-gibbous-6"
    elif moon_illumination <= 69:
        text += "waxing-gibbous-2" if waxing else "waning-gibbous-5"
    elif moon_illumination <= 76:
        text += "waxing-gibbous-3" if waxing else "waning-gibbous-4"
    elif moon_illumination <= 83:
        text += "waxing-gibbous-4" if waxing else "waning-gibbous-3"
    elif moon_illumination <= 90:
        text += "waxing-gibbous-5" if waxing else "waning-gibbous-2"
    elif moon_illumination <= 97:
        text += "waxing-gibbous-6" if waxing else "waning-gibbous-1"
    else:
        text += "full"
    return text

def get_weather_score(code: str) -> int:

    if code in LIGHTNING:
        return 7
    if code in SNOW:
        return 6
    if code in RAIN or code in HAIL:
        return 5
    if code in SHOWERS or code in SLEET or code in RAIN_MIX:
        return 4
    if code in FOG:
        return 3
    if code in VERY_CLOUDY or code in CLOUDY:
        return 2
    if code in PARTLY_CLOUDY:
        return 1
    if code in [113]:
        return 0

    return 0


def custom_weather_codes(old_code, time, sunrise, sunset, moonrise, moonset, temp, windspeed, cloudcover):
    old_code = str(old_code)
    time = int(time)
    sunrise = int(sunrise)
    sunset = int(sunset)
    moonrise = int(moonrise)
    moonset = int(moonset)
    temp = int(temp)
    windspeed = int(windspeed)
    cloudcover = int(cloudcover)
    
    code = {} # Zeit, Niederschlag, Wolken, Sonderfälle

    if sunrise <= time <= sunset:
        code["time"] = "day"
    else:
        code["time"] = "night-alt"

    if old_code in SHOWERS:
        code["precipitation"] = "showers"
    elif old_code in SNOW:
        code["precipitation"] = "snow"
    elif old_code in SLEET:
        code["precipitation"] = "sleet"
    elif old_code in RAIN_MIX:
        code["precipitation"] = "rain-mix"
    elif old_code in LIGHTNING:
        code["precipitation"] = "lightning"
    elif old_code in FOG:
        code["precipitation"] = "fog"
    elif old_code in RAIN:
        code["precipitation"] = "rain"
    elif old_code in HAIL:
        code["precipitation"] = "hail"
    else:
        code["precipitation"] = "none"

    if cloudcover <= 25:
        code["clouds"] = "clear"
    elif cloudcover <= 62:
        code["clouds"] = "light-cloudy"
    elif cloudcover <= 87:
        code["clouds"] = "cloudy"
    else:
        code["clouds"] = "overcast"
    
    if wind_to_beaufort(windspeed) >= 6:
        code["special"] = "strong-wind"
    elif wind_to_beaufort(windspeed) >= 4:
        code["special"] = "windy"
    elif temp >= 28:
        code["special"] = "hot"
    elif temp <= 4:
        code["special"] = "snowflake-cold"
    elif time - 70 <= sunrise <= time + 30:
        code["special"] = "sunrise"
    elif time - 70 <= sunset <= time + 30:
        code["special"] = "sunset"
    elif time - 70 <= moonrise <= time + 30 and code["time"] == "night-alt":
        code["special"] = "moonrise"
    elif time -70 <= moonset <= time + 30 and code["time"] == "night-alt":
        code["special"] = "moonset"
    elif time > moonset and time < moonrise and code["time"] == "night-alt":
            code["special"] = "stars"
    else:
        code["special"] = "none"

    code["old_code"] = old_code

    return code

def assign_icon(code):
    """returns Text of wi-Icons. See this site: https://weather-icons.dev"""
    text = "wi-"
    if code["precipitation"] != "none":
        if code["precipitation"] == "fog" and code["time"] == "night-alt":
            code["time"] = "night"
        if code["clouds"] in ["clear", "light-cloudy"]:
            text += code["time"] + "-"
        elif code["precipitation"] == "lightning":
            if code["old_code"] in ["389", "395"]:
                code["precipitation"] = "thunderstorm"
            else:
                code["precipitation"] = "storm-showers"
        
        text += code["precipitation"]
        
        if (code["special"] in ["windy", "strong-wind"] \
                and (text in ["wi-snow", "wi-rain"])) \
            or code["old_code"] in ["230", "305, 308", "338", "359"]:
            text += "-wind"

    else:
        if code["clouds"] == "cloudy":
            text += code["time"] + "-" + "cloudy"
            if code["special"] == "windy":
                text += "-gusts"

        elif code["clouds"] == "overcast":
            text += "cloudy"
            if code["special"] == "windy":
                text += "-gusts"
        
        elif code["special"] != "none":
            if code["special"] == "windy":
                if code["time"] == "day":
                    text += "day-windy"
                else:
                    text += "strong-wind"
            else:
                text += code["special"]

        elif code["clouds"] == "clear":
            if code["time"] == "day":
                text += "day-sunny"
            else:
                text += "night-clear"

        elif code["clouds"] == "light-cloudy":
            text += code["time"] + "-"
            if code["time"] == "day":
                text += "sunny-overcast"
            else:
                text += "night-alt-partly-cloudy"

    return text

def assign_colors(code):
    if code["precipitation"] in ["lightning", "thunderstorm", "storm-showers"]:
        return "text-orange-400"
    if code["precipitation"] in ["rain", "showers", "rain-mix"]:
        return "text-blue-400"
    if code["precipitation"] in ["snow", "sleet", "hail"]:
        return "text-white"
    if code["precipitation"] in ["fog"]:
        return "text-slate-300"
    
    if code["clouds"] in ["cloudy", "overcast"]:
        return "text-gray-200"
    
    if code["special"] in ["hot"]:
        return "text-orange-400"
    if code["special"] in ["snowflake-cold"]:
        return "text-cyan-400"
    if code["special"] in ["sunrise", "sunset", "stars"]:
        return "text-yellow-400"
    if code["special"] in ["windy", "strong-wind"]:
        return "text-blue-300"
    
    if code["clouds"] in ["clear", "light-cloudy"]:
        return "text-yellow-400"

    return "text-white"


def assign_icons(dayData: WeatherDataDay):
    """Not Used currently"""
    if not dayData.hourly:
        return
    for hour in dayData.hourly:
        text = assign_icon(hour.code)

BEAUFORT_LIMITS = [
    1, 5, 11, 19, 28, 38, 49, 61, 74, 88, 102, 117
]

def wind_to_beaufort(speed):
    speed = int(speed)
    for i, limit in enumerate(BEAUFORT_LIMITS):
        if speed <= limit:
            return i
    return 12


# main weather function
def get_weather(city:str):
    request_url = f"https://wttr.in/{city}?format=j1&lang=de"
    response = requests.get(
        request_url,
        timeout=5
    )
    data = response.json()

    current = data["current_condition"][0]
    current["sunrise"] = datetime.strptime(data["weather"][0]["astronomy"][0]["sunrise"], "%I:%M %p").strftime("%H%M").lstrip("0")
    current["sunset"] = datetime.strptime(data["weather"][0]["astronomy"][0]["sunset"], "%I:%M %p").strftime("%H%M").lstrip("0")
    current["moonrise"] = data["weather"][0]["astronomy"][0]["moonrise"]
    current["moonset"] = data["weather"][0]["astronomy"][0]["moonset"]
    if current["moonrise"] == "No moonrise":
        current["moonrise"] = "2400"
    else:
        current["moonrise"] = datetime.strptime(current["moonrise"], "%I:%M %p").strftime("%H%M").lstrip("0")
    if current["moonset"] == "No moonset":
        current["moonset"] = "0000"
    else:
        current["moonset"] = datetime.strptime(current["moonset"], "%I:%M %p").strftime("%H%M").lstrip("0")

    current["weatherCode"] = custom_weather_codes(
        current["weatherCode"],
        datetime.now().strftime("%H%M"),
        current["sunrise"],
        current["sunset"],
        current["moonrise"],
        current["moonset"],
        current["temp_C"],
        current["windspeedKmph"],
        current["cloudcover"]
    )

    ctext = assign_icon(current["weatherCode"])
    ccolor = assign_colors(current["weatherCode"])
    current["text"] = ctext + " " + ccolor

    forecast = []

    for day in data["weather"]:

        sunrise = datetime.strptime(day["astronomy"][0]["sunrise"], "%I:%M %p").strftime("%H%M").lstrip("0")
        sunset = datetime.strptime(day["astronomy"][0]["sunset"], "%I:%M %p").strftime("%H%M").lstrip("0")
        moonrise = day["astronomy"][0]["moonrise"]
        moonset = day["astronomy"][0]["moonset"]
        if moonrise == "No moonrise":
            moonrise = "2400"
        else:
            moonrise = datetime.strptime(moonrise, "%I:%M %p").strftime("%H%M").lstrip("0")
        if moonset == "No moonset":
            moonset = "2400"
        else:
            moonset = datetime.strptime(moonset, "%I:%M %p").strftime("%H%M").lstrip("0")

        moonphase = get_Moonphase(day["astronomy"][0]["moon_illumination"],day["astronomy"][0]["moon_phase"])

        dayData = WeatherDataDay(day["date"],
                                 sunrise, sunset,
                                 moonrise, moonset,
                                 day["astronomy"][0]["moon_phase"],
                                 day["maxtempC"], day["mintempC"],[])

        hourly = []
        print(f"\033[33m{day['date']}:\033[0m")
        for hour in day["hourly"]:

            hourData = WeatherDataHour(hour["time"],
                                       hour["weatherCode"],
                                       hour["lang_xx"][0]["value"],
                                       hour["tempC"],
                                       hour["windspeedKmph"],
                                       hour["cloudcover"])
            
            hourData.code = custom_weather_codes(
                hour["weatherCode"],
                hour["time"],
                sunrise,
                sunset,
                moonrise,
                moonset,
                hour["tempC"],
                hour["windspeedKmph"],
                hour["cloudcover"]
            )
            dayData.hourly.append(hourData)

            Weather_text = ""
            Weather_text += assign_icon(hourData.code)
            color = ""
            color += assign_colors(hourData.code)
            if color and Weather_text:
                Weather_text += " " + color

            wind_text = f"wi-wind-beaufort-{wind_to_beaufort(hour['windspeedKmph'])}"
            if wind_to_beaufort(hour['windspeedKmph']) <= 3:
                wind_text += " text-sky-200"
            elif wind_to_beaufort(hour['windspeedKmph']) <= 6:
                wind_text += " text-sky-400"
            elif wind_to_beaufort(hour['windspeedKmph']) <= 9:
                wind_text += " text-orange-200"
            else:
                wind_text += " text-orange-400"

            uvColor = ""
            if int(hour["uvIndex"]) <= 2:
                uvColor = "text-yellow-200"
            elif int(hour["uvIndex"]) <= 5:
                uvColor = "text-yellow-400"
            elif int(hour["uvIndex"]) <= 7:
                uvColor = "text-orange-400"
            elif int(hour["uvIndex"]) <= 10:
                uvColor = "text-red-400"
            else:
                uvColor = "text-purple-400"

            rainChance = ""
            if int(hour['chanceofrain']) < int(hour['chanceofsnow']):
                rainChance += f"{hour['chanceofnow']}% Schnee"
            else:
                rainChance += f"{hour['chanceofrain']}% Regen"

            precipMM = float(hour['precipMM'])
            if precipMM > 10:
                precipMM_text = f"{precipMM/10:.1f} cm"
            else:
                precipMM_text = f"{precipMM:.1f} mm"

            #print(f"{hourData.time:>4}: {text:<35} | {hourData.code}")

            if hour["time"] in ["0", "300"]:
                if not (int(datetime.now().strftime("%H%M")) >= 2230 or int(datetime.now().strftime("%H%M")) <= 430):
                    continue
            hourly.append({
                "time": hour["time"],
                "temp": hour["tempC"],
                "desc": hour["lang_xx"][0]["value"],
                "code": hour["weatherCode"],
                "windspeed": hour["windspeedKmph"],
                "windspeedtext": wind_text,
                "text": Weather_text,
                "rainChance": rainChance,
                "precipMM": precipMM_text,
                "uvIndex": hour["uvIndex"],
                "uvColor": uvColor,
                "visibility": hour["visibility"],
                "windDir": hour["winddir16Point"]
            })

        # dominance calculation
        scores = {}

        for hour in hourly:
            code = hour["code"]
            score = get_weather_score(code)

            if code not in scores:
                scores[code] = 0

            base = (
                3 if hour["time"] in ["900", "1200", "1500"]
                else 2 if hour["time"] == "1800"
                else 1
            )

            scores[code] += base + score * 0.5

        dominant_code = max(scores, key=lambda k: scores[k])
        dominant_desc = next(h["desc"] for h in hourly if h["code"] == dominant_code)

        dominant_data = WeatherDataHour(
            0,
            dominant_code,
            dominant_desc,
            0.0,
            0.0,
            0.0
        )
        count = 0

        for hour in dayData.hourly:
            if hour.code["old_code"] == dominant_code:
                if int(hour.time) < 600:
                    continue
                count += 1
                dominant_data.time += int(hour.time)
                dominant_data.temp += int(hour.temp)
                dominant_data.windspeed += int(hour.windspeed)
                dominant_data.cloudcover += int(hour.cloudcover)

        dominant_data.time = dominant_data.time // count
        dominant_data.time = dominant_data.time - 20 if dominant_data.time % 100 == 50 else dominant_data.time
        dominant_data.temp = round(dominant_data.temp / count)
        dominant_data.windspeed = round(dominant_data.windspeed / count)
        dominant_data.cloudcover = round(dominant_data.cloudcover / count)

        print(f"Dominant WeatherData: {dominant_data.to_dict()}")

        dominant_code = custom_weather_codes(
            dominant_code,
            dominant_data.time,
            sunrise, sunset,
            moonrise, moonset,
            dominant_data.temp,
            dominant_data.windspeed,
            dominant_data.cloudcover
        )
        print(dominant_code)
        dominant_text = assign_icon(dominant_code) + " " + assign_colors(dominant_code)

        print(f"\033[1mDominant code\033[0m: {dominant_code["old_code"]}: \033[32m{dominant_desc}\033[0m | Icon: \033[34m{dominant_text}\033[0m | {scores}")

        # Sort moontimes
        if day["astronomy"][0]["moonrise"] == "No moonrise":
            moontime_1 = "----"
            moontime_2 = moonset
            moontime_1_icon = "wi-moonrise"
            moontime_2_icon = "wi-moonset"
        elif day["astronomy"][0]["moonset"] == "No moonset":
            moontime_1 = moonrise
            moontime_2 = "----"
            moontime_1_icon = "wi-moonrise"
            moontime_2_icon = "wi-moonset"
        elif day["astronomy"][0]["moonrise"] == "No moonrise" and day["astronomy"][0]["moonset"] == "No moonset":
            moontime_1 = "----"
            moontime_2 = "----"
            moontime_1_icon = "wi-moonrise"
            moontime_2_icon = "wi-moonset"
        elif int(moonrise) < int(moonset):
            moontime_1 = moonrise
            moontime_2 = moonset
            moontime_1_icon = "wi-moonrise"
            moontime_2_icon = "wi-moonset"
        else:
            moontime_1 = moonset
            moontime_2 = moonrise
            moontime_1_icon = "wi-moonset"
            moontime_2_icon = "wi-moonrise"

        forecast.append({
            "date": day["date"],
            "max": day["maxtempC"],
            "min": day["mintempC"],
            "desc": dominant_desc,
            "code": dominant_code["old_code"],
            "text": dominant_text,
            "hourly": hourly,
            "sunrise": sunrise,
            "sunset": sunset,
            "moontime_1": {"time": moontime_1, "icon": moontime_1_icon},
            "moontime_2": {"time": moontime_2, "icon": moontime_2_icon},
            "moonphase": moonphase,
        })

    print()
    return {
        "current": {
            "temp": current["temp_C"],
            "desc": current["lang_xx"][0]["value"],
            "code": current["weatherCode"],
            "text": current["text"]
        },
        "forecast": forecast
    }
