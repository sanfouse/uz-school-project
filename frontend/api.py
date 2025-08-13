import os
import json
from typing import Any, Dict, List, Optional
import requests

DEFAULT_TIMEOUT = float(os.getenv("SCRAPERS_API_TIMEOUT", "10"))
BASE_URL = os.getenv("SCRAPERS_API_BASE", "http://scrapers-api:8000").rstrip("/")


def _url(path: str) -> str:
    return f"{BASE_URL}{path}"


def health() -> Dict[str, Any]:
    try:
        r = requests.get(_url("/health"), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return {
            "ok": True,
            "data": (
                r.json()
                if r.headers.get("content-type", "").startswith("application/json")
                else r.text
            ),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def start_scraper(job_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    payload = {"job_id": job_id, **params}
    try:
        r = requests.post(_url("/start-scraper"), json=payload, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return {"ok": True, "data": r.json()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def stop_scraper(job_id: str) -> Dict[str, Any]:
    try:
        r = requests.delete(_url(f"/stop-scraper/{job_id}"), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return {
            "ok": True,
            "data": (
                r.json()
                if r.headers.get("content-type", "").startswith("application/json")
                else r.text
            ),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def list_jobs() -> Dict[str, Any]:
    try:
        r = requests.get(_url("/jobs"), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        jobs = data.get("jobs", []) if isinstance(data, dict) else []
        return {"ok": True, "data": jobs}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_job_logs(job_name: str, tail: Optional[int] = None) -> Dict[str, Any]:
    params = {"tail": tail} if tail else None
    try:
        r = requests.get(
            _url(f"/job/{job_name}/logs"), params=params, timeout=DEFAULT_TIMEOUT
        )
        r.raise_for_status()
        return {"ok": True, "data": r.json()['logs']}
    except Exception as e:
        return {"ok": False, "error": str(e)}
