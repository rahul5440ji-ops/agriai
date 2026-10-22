"""FastAPI application factory for AgriAI.

ML training code is kept out of request handlers — inference only.
"""
import logging
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.database import engine
from backend.models import Base  # noqa: F401  ensures metadata is registered
from backend.routers.health import router as health_router
from backend.routers.farms import router as farms_router
from backend.routers.yield_pred import router as yield_router
from backend.routers.markets import router as markets_router
from backend.routers.price import router as price_router

settings = get_settings()

# Logging — never log secrets or PII
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("agriai")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AgriAI API",
        version="0.1.0",
        description="AI/ML decision support for Indian farmers",
    )

    # CORS — restrict to configured origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Structured error responses — never expose stack traces or paths
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": request.url.path,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "status_code": 500,
                "detail": "Internal server error",
                "path": request.url.path,
            },
        )

    # Routers
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(farms_router, prefix="/api/v1")
    app.include_router(yield_router, prefix="/api/v1")
    app.include_router(markets_router, prefix="/api/v1")
    app.include_router(price_router, prefix="/api/v1")

    return app


app = create_app()


def main():  # pragma: no cover
    import uvicorn
    uvicorn.run(
        "backend.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,
    )


if __name__ == "__main__":  # pragma: no cover
    main()