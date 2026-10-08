"""
Main FastAPI application entrypoint for FloodSentinel.
"""

import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from api.config import settings
from api.routes.health import router as health_router
from api.routes.rainfall import router as rainfall_router
from api.routes.overflow import router as overflow_router
from api.routes.alerts import router as alerts_router
from api.routes.demo import router as demo_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("floodsentinel.api")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "FloodSentinel REST API for real-time urban flood risk inference, "
        "meteorological rainfall forecasting (XGBoost + LSTM), underground drainage "
        "overflow onset prediction (XGBoost), and multi-modal risk fusion."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Clean structured error response for validation failures."""
    errors = []
    for err in exc.errors():
        field_loc = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({
            "field": field_loc,
            "message": err.get("msg", "Invalid value"),
            "type": err.get("type", "value_error"),
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "The request payload failed validation.",
            "details": errors,
        },
    )


# Root route
@app.get("/", tags=["General"], summary="API Root")
def get_root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "documentation": "/docs",
        "endpoints": {
            "health": f"{settings.api_prefix}/health",
            "rainfall_predict": f"{settings.api_prefix}/risk/predict",
            "overflow_predict": f"{settings.api_prefix}/risk/overflow",
            "risk_rank": f"{settings.api_prefix}/alerts/rank",
            "demo_risk": f"{settings.api_prefix}/demo/risk",
        },
    }


# Include Routers
app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(rainfall_router, prefix=settings.api_prefix)
app.include_router(overflow_router, prefix=settings.api_prefix)
app.include_router(alerts_router, prefix=settings.api_prefix)
app.include_router(demo_router, prefix=settings.api_prefix)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=settings.host, port=settings.port, reload=True)
