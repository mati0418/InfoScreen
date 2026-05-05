from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
import json

app = FastAPI()

@app.get("/")
def serve_index():
    return FileResponse("index.html")

def get_weather_score(code: str) -> int:
    if int(code) in [200, 386, 389]:  # Gewitter
        return 6
    if 176 <= int(code) <= 308:       # Regen
        return 5
    if 323 <= int(code) <= 338:       # Schnee
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
    #print(json.dumps(data, indent=2))
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


        forecast.append({
            "date": day["date"],
            "max": day["maxtempC"],
            "min": day["mintempC"],
            "desc": dominant_desc,
            "code": dominant_code,
            "hourly": hourly
        })

    return {
        "current": {
            "temp": current["temp_C"],
            "desc": current["lang_de"][0]["value"],
            "code": current["weatherCode"]
        },
        "forecast": forecast

    }