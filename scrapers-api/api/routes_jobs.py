from fastapi import APIRouter
from kubernetes.client import ApiException

from services.k8s import list_jobs, delete_job, get_job_logs
from services.responses import response_ok, response_error

router = APIRouter(tags=["jobs"])


@router.delete("/stop-scraper/{job_id}")
async def stop_scraper(job_id: str):
    job_name = f"profi-scraper-job-{job_id}"
    try:
        delete_job(job_name)
        return response_ok(
            job_id=job_id, message=f"Scraper job {job_id} stopped successfully"
        )
    except ApiException as e:
        if e.status == 404:
            response_error(f"Job {job_id} not found", 404)
        response_error(f"Failed to stop scraper: {e}")
    except Exception as e:
        response_error(f"Failed to stop scraper: {e}")


@router.get("/jobs")
async def get_jobs(prefix: str | None = None, status: str | None = None):
    try:
        jobs = list_jobs(prefix=prefix, status=status)
        return response_ok(
            jobs=[
                {
                    "name": job.metadata.name,
                    "status": (
                        "running"
                        if job.status.active
                        else (
                            "finished"
                            if (job.status.succeeded or job.status.failed)
                            else "pending"
                        )
                    ),
                    "start_time": job.status.start_time,
                    "completion_time": job.status.completion_time,
                }
                for job in jobs
            ]
        )
    except Exception as e:
        response_error(f"Failed to list jobs: {e}")


@router.get("/job/{job_name}/logs")
async def get_job_logs_endpoint(job_name: str):
    try:
        logs = get_job_logs(job_name)
        return response_ok(job_name=job_name, logs=logs)
    except Exception as e:
        response_error(f"Failed to get job logs: {e}")
