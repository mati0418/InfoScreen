
class WeatherDataHour:

    def __init__(self, time, code, desc, temp, windspeed, cloudcover) -> None:
        self.time = time
        self.code = code
        self.desc = desc
        self.temp = temp
        self.windspeed = windspeed
        self.cloudcover = cloudcover

    def to_dict(self):
        return {
            "time": self.time,
            "code": self.code,
            "desc": self.desc,
            "temp": self.temp,
            "windspeed": self.windspeed,
            "cloudcover": self.cloudcover
        }


class WeatherDataDay:

    hourly: list[WeatherDataHour] = []
    code: int|None = None
    
    def __init__(self, date, sunrise, sunset, moonrise, moonset, moonphase, maxtemp, mintemp, hourly:list = []) -> None:
        self.date = date
        self.sunrise = sunrise
        self.sunset = sunset
        self.moonrise = moonrise
        self.moonset = moonset
        self.moonphase = moonphase
        self.maxtemp = maxtemp
        self.mintemp = mintemp
        self.hourly = hourly

    def to_dict(self):
        return {
            "date": self.date,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
            "moonrise": self.moonrise,
            "moonset": self.moonset,
            "moonphase": self.moonphase,
            "maxtemp": self.maxtemp,
            "mintemp": self.mintemp,
            "hourly": [h.to_dict() for h in self.hourly ] if self.hourly else None
        }