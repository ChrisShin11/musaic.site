from pydantic import BaseModel
from typing import Optional, List

class MusicRecommendationRequest(BaseModel):
    """Request model for music recommendation"""
    spotify_token: str
    playlist_name: Optional[str] = None

class DiverseTrack(BaseModel):
    """Model for a diverse track suggestion"""
    song: str
    artist: str
    year: int
    context: str

class GeminiMusicRecommendation(BaseModel):
    """Model for Gemini AI music recommendation response with diverse tracks"""
    seed_track: dict  # Contains 'song' and 'artist'
    playlist_name: str
    music_genre: str
    diverse_tracks: List[DiverseTrack]

class MusicRecommendationResponse(BaseModel):
    """Response model for music recommendation"""
    playlist_url: str
    playlist_name: str
    tracks_added: int
    seed_track: Optional[dict] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
