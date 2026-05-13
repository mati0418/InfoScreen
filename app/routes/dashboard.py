from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/")
def serve_index():
    return FileResponse("app/templates/dashboard.html")