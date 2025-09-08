import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Spotify API Configuration
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    SPOTIFY_REDIRECT_URI: str = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:5173/callback")
    SPOTIFY_SCOPE: str = "playlist-modify-public user-read-private user-read-email playlist-modify-private user-library-read user-top-read user-read-recently-played"
    
    # Image Processing Configuration
    IMAGE_TARGET_SIZE: tuple = (300, 300)
    IMAGE_MAX_SIZE_KB: int = 256
    IMAGE_QUALITY: int = 85
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = int(os.getenv("PORT", 8080))
    
    # Frontend Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173/")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
