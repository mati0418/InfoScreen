import requests
from datetime import datetime


def get_weather_score(code: str) -> int:
    code = int(code) # pyright: ignore

    if code in [200, 386, 389, 392]:
        return 7    # z.b. Gewitter
    if code in [299, 302, 305, 308, 356, 359]:
        return 6    # z.b. Regen
    if code in [230, 329, 332, 335, 338, 371, 395]:
        return 5    # z.b. Schnee
    if code in [176, 179, 182, 185, 227, 263, 266, 281,
                284, 293, 296, 311, 314, 317, 320, 323,
                326, 350, 353, 362, 365, 368, 374, 377, 502]:
        return 4   # z.b. leichter Regen / leichter Schnee
    if code in [143, 248, 260, 500, 501]:
        return 3    # z.b. Nebel
    if code in [119, 122, 504]:
        return 2    # z.b. bewölkt
    if code in [116, 503]:
        return 1    # z.b. teilweise bewölkt
    if code in [113, 510, 511, 512]:
        return 0    # z.b. sonnig

    return 0


def custom_weather_codes(code, time, sunrise, sunset, moonrise, moonset, temp, windspeed):
    if code == "113":   # sonnig
        if (int(time) - 70 <= int(sunrise) <= int(time) + 30):
            return "510"  # Sonnenaufgang
        elif (int(time) - 70 <= int(sunset) <= int(time) + 30):
            return "511"  # Sonnenuntergang
        elif (int(time) + 30 >= int(moonset) or int(time) - 70 <= int(moonrise)) and not int(sunrise) <= int(time) <= int(sunset):
            return "512"  # klare mondlose Nacht
        elif int(windspeed) >= 20 and int(sunrise) <= int(time) <= int(sunset):
            return "503" if int(windspeed) < 30 else "502"  # windig oder stürmisch
        elif int(temp) >= 28 and int(sunrise) <= int(time) <= int(sunset):
            return "500"  # heiß
        elif int(temp) <= 3 and int(sunrise) <= int(time) <= int(sunset):
            return "501"  # kalt

    elif code == "116":   # leicht bewölkt
        if (int(time) - 70 <= int(sunrise) <= int(time) + 30):
            return "510"  # Sonnenaufgang
        elif (int(time) - 70 <= int(sunset) <= int(time) + 30):
            return "511"  # Sonnenuntergang
        elif int(windspeed) >= 20:
            return "504" if int(windspeed) < 30 else "502"  # windig oder stürmisch
        elif int(temp) >= 28 and int(sunrise) <= int(time) <= int(sunset):
            return "500"  # heiß
        elif int(temp) <= 3 and int(sunrise) <= int(time) <= int(sunset):
            return "501"  # kalt

    elif code == "119":   # bewölkt
        if int(windspeed) >= 20:
            return "504" if int(windspeed) < 30 else "502"  # windig oder stürmisch

    return code



# main weather function
def get_weather():
    response = requests.get(
        "https://wttr.in/Ilmenau?format=j1&lang=de",
        timeout=5
    )
    data = response.json()

    current = data["current_condition"][0]
    curr_sunrise = data["weather"][0]["astronomy"][0]["sunrise"]
    curr_sunset = data["weather"][0]["astronomy"][0]["sunset"]
    curr_moonrise = data["weather"][0]["astronomy"][0]["moonrise"]
    curr_moonset = data["weather"][0]["astronomy"][0]["moonset"]
    if curr_moonrise == "No moonrise":
        curr_moonrise = "24:00 AM"
    if curr_moonset == "No moonset":
        curr_moonset = "00:00 AM"

    current["weatherCode"] = custom_weather_codes(
        current["weatherCode"],
        datetime.now().strftime("%H%M"),
        datetime.strptime(curr_sunrise, "%I:%M %p").strftime("%H%M").lstrip("0"),
        datetime.strptime(curr_sunset, "%I:%M %p").strftime("%H%M").lstrip("0"),
        datetime.strptime(curr_moonrise, "%I:%M %p").strftime("%H%M").lstrip("0"),
        datetime.strptime(curr_moonset, "%I:%M %p").strftime("%H%M").lstrip("0"),
        current["temp_C"],
        current["windspeedKmph"]
    )

    forecast = []

    for day in data["weather"]:

        sunrise = datetime.strptime(day["astronomy"][0]["sunrise"], "%I:%M %p").strftime("%H%M").lstrip("0")
        sunset = datetime.strptime(day["astronomy"][0]["sunset"], "%I:%M %p").strftime("%H%M").lstrip("0")
        moonrise = datetime.strptime(day["astronomy"][0]["moonrise"], "%I:%M %p").strftime("%H%M").lstrip("0")
        moonset = datetime.strptime(day["astronomy"][0]["moonset"], "%I:%M %p").strftime("%H%M").lstrip("0")

        hourly = []

        for hour in day["hourly"]:
            if hour["time"] in ["0", "300"]:
                continue

            hour["weatherCode"] = custom_weather_codes(
                hour["weatherCode"],
                hour["time"],
                sunrise,
                sunset,
                moonrise,
                moonset,
                hour["tempC"],
                hour["windspeedKmph"]
            )

            hourly.append({
                "time": hour["time"],
                "temp": hour["tempC"],
                "desc": hour["lang_xx"][0]["value"],
                "code": hour["weatherCode"],
                "wind": hour["windspeedKmph"]
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
                else 1 if hour["time"] == "1800"
                else 1 / 3
            )

            scores[code] += base + score * 0.5

        dominant_code = max(scores, key=lambda k: scores[k])
        dominant_desc = next(h["desc"] for h in hourly if h["code"] == dominant_code)

        forecast.append({
            "date": day["date"],
            "max": day["maxtempC"],
            "min": day["mintempC"],
            "desc": dominant_desc,
            "code": dominant_code,
            "hourly": hourly,
            "sunrise": sunrise,
            "sunset": sunset
        })

    return {
        "current": {
            "temp": current["temp_C"],
            "desc": current["lang_xx"][0]["value"],
            "code": current["weatherCode"]
        },
        "forecast": forecast
    }
