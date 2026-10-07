from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router

app = FastAPI(
    title="GamePriceTracker API",
    description="Сервис для трекинга цен на игры",
    version="1.0.0",
)

app.include_router(api_v1_router)


@app.get("/")
async def root():
    return {"message": "GamePriceTracker API is running"}
