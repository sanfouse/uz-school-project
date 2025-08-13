from fastapi import FastAPI
from api import routes_scrapers, routes_jobs, routes_health

app = FastAPI(title="Scrapers API")

app.include_router(routes_scrapers.router)
app.include_router(routes_jobs.router)
app.include_router(routes_health.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, port=8000, host="0.0.0.0")
