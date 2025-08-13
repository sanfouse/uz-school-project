import uuid
from fastapi import APIRouter
from core.redis_client import save_scraper_config
from models.scraper_config import ScraperConfig
from services.job_env import make_env_vars
from services.k8s import create_job
from services.responses import response_ok, response_error

router = APIRouter(tags=["scrapers"])


@router.post("/start-scraper")
async def start_scraper(config: ScraperConfig):
    job_id = config.job_id
    try:
        await save_scraper_config(job_id, config.model_dump())
        env_vars = make_env_vars(job_id, config)

        create_job(
            job_name=f"profi-scraper-job-{job_id}",
            container_name=f"profi-scraper-{config.profi_login.lower() or 'default'}",
            image="profi-scraper:latest",
            env_vars=env_vars,
        )

        return response_ok(
            job_id=job_id, message=f"Scraper job {job_id} started successfully"
        )
    except Exception as e:
        response_error(f"Failed to start scraper: {e}")
