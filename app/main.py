from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import logger
from app.core.exceptions import exception_handler
from app.db.mongodb import connect_to_mongodb, close_mongodb_connection
from app.db.init_db import init_db

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add event handlers
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Starting up application...")
    await connect_to_mongodb()
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down application...")
    await close_mongodb_connection()


# Add global exception handler
@app.exception_handler(Exception)
async def handle_exception(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    return await exception_handler(request, exc)


# Add API router
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}