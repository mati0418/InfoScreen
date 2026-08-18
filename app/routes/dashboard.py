from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/weather/{city}")
async def serve_index(request: Request, city: str):
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"request": request, "city": city}
    )