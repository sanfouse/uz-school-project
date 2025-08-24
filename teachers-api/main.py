from contextlib import asynccontextmanager

from fastapi import FastAPI


from routers import lessons, teachers, invoices


app = FastAPI(title="Lessons API")

app.include_router(teachers.router)
app.include_router(lessons.router)
app.include_router(invoices.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
