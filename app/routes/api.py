from fastapi import APIRouter
from app.services.weather_data import get_weather

router = APIRouter()

@router.get("/weather")
def weather():
    return get_weather()