import socket

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.router import api_router
from src.core.config import get_settings
from src.db.mongodb import connect_to_mongodb, close_mongodb_connection

from src.core.logging import logger

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
)

# Add CORS middleware with comprehensive origins support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Production origins
        "https://thirteenk.co.za",
        "https://thirteenk-frontend-service-227629318480.us-central1.run.app",
        "https://api.thirteenk.co.za",
        "https://thirteenkapi-service-227629318480.us-central1.run.app",
        # Local development origins
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # Important for downloads
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event():
    await connect_to_mongodb()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongodb_connection()


@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.APP_VERSION,
        "api_url": settings.API_PREFIX,
        "docs": f"{settings.API_PREFIX}/docs",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(settings.PORT) or 8080
    try:
        # Update this section to use a different event loop policy on Windows
        import platform

        if platform.system() == 'Windows':
            import asyncio

            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            reload=settings.DEBUG,
            workers=1,
            loop="auto"  # Changed from "asyncio" to "auto"
        )
    except Exception as e:
        logger.error(f"Server error: {e}")
        # Force cleanup of any remaining sockets
        import gc

        for obj in gc.get_objects():
            if isinstance(obj, socket.socket):
                try:
                    if obj.fileno() != -1:  # Make sure the socket is valid
                        obj.close()
                except:
                    pass