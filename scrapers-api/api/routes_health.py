from fastapi import APIRouter
from services.responses import response_ok

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return response_ok(status="healthy")
