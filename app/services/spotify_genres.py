"""
Spotify genres service - provides valid Spotify genres
Since the Spotify API endpoint for genre seeds has been deprecated,
we maintain a curated list of valid Spotify genres.
"""

from typing import List
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Curated list of valid Spotify genres (as of 2024)
# This list is based on genres that were previously available through the API
# and commonly used in Spotify's recommendation system
VALID_SPOTIFY_GENRES = [
    "acoustic",
    "afrobeat", 
    "alt-rock",
    "alternative",
    "ambient",
    "anime",
    "black-metal",
    "bluegrass",
    "blues",
    "bossanova",
    "brazil",
    "breakbeat",
    "british",
    "cantopop",
    "chicago-house",
    "children",
    "chill",
    "classical",
    "club",
    "comedy",
    "country",
    "dance",
    "dancehall",
    "death-metal",
    "deep-house",
    "detroit-techno",
    "disco",
    "disney",
    "drum-and-bass",
    "dub",
    "dubstep",
    "edm",
    "electro",
    "electronic",
    "emo",
    "folk",
    "forro",
    "french",
    "funk",
    "garage",
    "german",
    "gospel",
    "goth",
    "grindcore",
    "groove",
    "grunge",
    "guitar",
    "happy",
    "hard-rock",
    "hardcore",
    "hardstyle",
    "heavy-metal",
    "hip-hop",
    "holidays",
    "honky-tonk",
    "house",
    "idm",
    "indian",
    "indie",
    "indie-pop",
    "industrial",
    "iranian",
    "j-dance",
    "j-idol",
    "j-pop",
    "j-rock",
    "jazz",
    "k-pop",
    "kids",
    "latin",
    "latino",
    "malay",
    "mandopop",
    "metal",
    "metal-misc",
    "metalcore",
    "minimal-techno",
    "movies",
    "mpb",
    "new-age",
    "new-release",
    "opera",
    "pagode",
    "party",
    "philippines-opm",
    "piano",
    "pop",
    "pop-film",
    "post-dubstep",
    "power-pop",
    "progressive-house",
    "psych-rock",
    "punk",
    "punk-rock",
    "r-n-b",
    "rainy-day",
    "reggae",
    "reggaeton",
    "road-trip",
    "rock",
    "rock-n-roll",
    "rockabilly",
    "romance",
    "sad",
    "salsa",
    "samba",
    "sertanejo",
    "show-tunes",
    "singer-songwriter",
    "ska",
    "sleep",
    "songwriter",
    "soul",
    "soundtracks",
    "spanish",
    "study",
    "summer",
    "swedish",
    "synth-pop",
    "tango",
    "techno",
    "trance",
    "trip-hop",
    "turkish",
    "work-out",
    "world-music"
]

class SpotifyGenresService:
    """Service for managing Spotify genres"""
    
    @staticmethod
    def get_available_genres() -> List[str]:
        """
        Get list of available Spotify genres
        
        Returns:
            List of valid Spotify genre strings
        """
        logger.info(f"Retrieved {len(VALID_SPOTIFY_GENRES)} valid Spotify genres")
        return VALID_SPOTIFY_GENRES.copy()
    
    @staticmethod
    def is_valid_genre(genre: str) -> bool:
        """
        Check if a genre is valid for Spotify recommendations
        
        Args:
            genre: Genre string to validate
            
        Returns:
            True if genre is valid, False otherwise
        """
        return genre.lower() in [g.lower() for g in VALID_SPOTIFY_GENRES]
    
    @staticmethod
    def get_genres_by_category() -> dict:
        """
        Get genres organized by category
        
        Returns:
            Dictionary with genre categories as keys and lists of genres as values
        """
        categories = {
            "Electronic": ["electronic", "edm", "house", "techno", "trance", "dubstep", "ambient", "chill"],
            "Rock": ["rock", "alternative", "indie", "punk", "metal", "grunge", "hard-rock", "progressive-house"],
            "Pop": ["pop", "indie-pop", "synth-pop", "power-pop", "k-pop", "j-pop"],
            "Hip-Hop": ["hip-hop", "rap", "trap", "r-n-b"],
            "Jazz": ["jazz", "blues", "soul", "funk"],
            "Classical": ["classical", "opera", "piano"],
            "World": ["world-music", "latin", "reggae", "salsa", "bossa-nova"],
            "Mood": ["happy", "sad", "chill", "party", "romance", "work-out"],
            "Decade": ["disco", "funk", "new-wave", "grunge"],
            "Instrumental": ["acoustic", "guitar", "piano", "instrumental"]
        }
        return categories
    
    @staticmethod
    def search_genres(query: str) -> List[str]:
        """
        Search for genres matching a query
        
        Args:
            query: Search query string
            
        Returns:
            List of genres matching the query
        """
        query_lower = query.lower()
        matching_genres = [genre for genre in VALID_SPOTIFY_GENRES 
                          if query_lower in genre.lower()]
        return matching_genres
    
    @staticmethod
    def get_popular_genres() -> List[str]:
        """
        Get a list of commonly used/popular genres
        
        Returns:
            List of popular genre strings
        """
        popular_genres = [
            "pop", "rock", "hip-hop", "electronic", "indie", "alternative",
            "r-n-b", "jazz", "classical", "country", "folk", "blues",
            "reggae", "latin", "world-music", "ambient", "chill", "dance"
        ]
        return popular_genres
