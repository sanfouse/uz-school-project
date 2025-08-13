from fastapi import HTTPException
from typing import Any


def response_ok(**kwargs) -> dict[str, Any]:
    return {"status": "success", **kwargs}


def response_error(message: str, status_code: int = 500):
    raise HTTPException(status_code=status_code, detail=message)
