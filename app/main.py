from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Musaic - AI Music Recommendation API",
    description="An API that recommends music based on images using Gemini AI and Spotify",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    import os
    port = os.getenv("PORT", 8080)
    logger.info("Starting Musaic API...")
    logger.info(f"Port from environment: {port}")
    logger.info(f"API will be available at http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info("Startup complete - ready to serve requests")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Musaic API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
