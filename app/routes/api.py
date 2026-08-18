from fastapi import APIRouter
from app.services.weather_data import get_weather

router = APIRouter()

@router.get("/weatherdata/{city}")
def weather(city: str):
    return get_weather(city)