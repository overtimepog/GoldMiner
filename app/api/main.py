from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from app.db.database import init_db
from app.db.migrate import run_migrations
from app.api.routers import ideas, validation, research, pain_points
from app.api.websocket import websocket_endpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up GoldMiner API...")
    try:
        # Run migrations first
        run_migrations()
    except Exception as e:
        logger.error(f"Migration error: {e}")
    # Initialize database
    init_db()
    yield
    # Shutdown
    logger.info("Shutting down GoldMiner API...")

# Create FastAPI app
app = FastAPI(
    title="GoldMiner API",
    description="AI-powered startup idea generation and validation system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include routers
app.include_router(ideas.router)
app.include_router(validation.router)
app.include_router(research.router)
app.include_router(pain_points.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to GoldMiner API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "ideas": "/api/ideas",
            "validation": "/api/validation",
            "research": "/api/research",
            "pain-points": "/api/pain-points",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    await websocket_endpoint(websocket)