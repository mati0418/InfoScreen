from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
from datetime import datetime
import json

app = FastAPI()

@app.get("/")
def serve_index():
    return FileResponse("index.html")

def get_weather_score(code: str) -> int:
    if int(code)  in [200, 386, 389, 392]:    # Gewitter
        return 7
    if int(code) in [299, 302, 305, 308, 356, 359]:  # Regen
        return 6
    if int(code) in [230, 329, 332, 335, 338, 371, 395]:       # Schnee
        return 5
    if int(code) in [176, 179, 182, 185, 227, 263, 266, 281, 
                     284, 293, 296, 311, 314, 317, 320, 323, 
                     326, 350, 353, 362, 365, 368, 374, 377]:       # leichter Regen oder leichter Schnee
        return 4
    if int(code) in [143, 248, 260]:  # Nebel
        return 3
    if int(code) in [119, 122]:       # bewölkt
        return 2
    if int(code) == 116:              # teilweise bewölkt
        return 1
    if int(code) == 113:              # sonnig
        return 0

    return 0

@app.get("/weather")
def get_weather():
    response = requests.get("https://wttr.in/Ilmenau?format=j1&lang=de")
    data = response.json()

    current = data["current_condition"][0]
    print(json.dumps(current, indent=2))
    #print("Current Weather:", current["weatherDesc"][0]["value"])
    #print("Morgen:")
    day = data["weather"][1]  # mittags
    for hour in day["hourly"]:
        #print(hour["FeelsLikeC"])
        #print(hour["chanceofrain"])
        #print(hour["lang_de"][0]["value"])
        #print(hour["tempC"])
        #print(hour["time"])
        #print(hour["uvIndex"])
        #print(hour["weatherCode"], type(hour["weatherCode"]))
        #print()
        pass
    

    forecast = []
    for day in data["weather"]:
        hourly = []
        for hour in day["hourly"]:
            if hour["time"] in ["0", "300"]:
                continue
            hourly.append({
                "time": hour["time"],
                "temp": hour["tempC"],
                "desc": hour["lang_de"][0]["value"],
                "code": hour["weatherCode"]
            })

        #avg_temp = (sum(int(hourly[i]["temp"]) for i in range(len(hourly))) / len(hourly)) if hourly else 0
        scores = {}
        for hour in hourly:
            code = hour["code"]
            score = get_weather_score(hour["code"])
            if code not in scores:
                scores[code] = 0
            scores[code] += 3 + score *0.5
        dominant_code = max(scores, key=lambda k: scores[k])
        dominant_desc = next(hour["desc"] for hour in hourly if hour["code"] == dominant_code)

        sunrise = datetime.strptime(day["astronomy"][0]["sunrise"], "%I:%M %p").strftime("%H%M").lstrip("0")
        sunset = datetime.strptime(day["astronomy"][0]["sunset"], "%I:%M %p").strftime("%H%M").lstrip("0")

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
            "desc": current["lang_de"][0]["value"],
            "code": current["weatherCode"]
        },
        "forecast": forecast

    }