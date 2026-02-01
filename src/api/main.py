from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import (
    auth,
    booking_rules,
    bookings,
    businesses,
    call_logs,
    health,
    knowledge_base,
    services,
    voice_gateway,
)
from src.shared.errors import AppError

app = FastAPI(title="Voice Agent Healthcare", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(businesses.router)
app.include_router(services.router)
app.include_router(booking_rules.router)
app.include_router(bookings.router)
app.include_router(knowledge_base.router)
app.include_router(call_logs.router)
app.include_router(voice_gateway.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
