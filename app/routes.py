from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from PIL import Image
from io import BytesIO
from app.services.gemini import GeminiService
from app.services.spotify import SpotifyService
from app.models import MusicRecommendationResponse, ErrorResponse, HealthResponse
from app.utils.logger import get_logger
from app.config import settings
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import Optional

logger = get_logger(__name__)
router = APIRouter()

# Initialize Gemini service (no auth needed)
gemini_service = GeminiService()

@router.post("/recommend_music", response_model=MusicRecommendationResponse)
async def recommend_music(
    file: UploadFile = File(...),
    spotify_token: str = Form(...),
    playlist_name: Optional[str] = Form(None)
):
    """
    Recommend music based on an uploaded image using user's Spotify account and music history.
    
    Args:
        file: Image file to analyze
        spotify_token: User's Spotify access token
        playlist_name: Optional custom playlist name
        
    Returns:
        JSON response with playlist URL, name, and track count
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        # Check if file is an image
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        logger.info(f"Processing image: {file.filename} for user with token")
        
        # Initialize Spotify service with user token
        spotify_service = SpotifyService(user_token=spotify_token)
        
        # Read and process the image
        image_data = await file.read()
        image = Image.open(BytesIO(image_data))
        
        # Process image with Gemini service
        full_image_data, thumbnail_data = gemini_service.process_image(image)
        
        # Step 1: Analyze image for seed track
        seed_track_info = gemini_service.analyze_image_for_seed_track(full_image_data)
        
        # Step 2: Get diverse tracks using Spotify's audio analysis (no LLM hallucination!)
        seed_track_id = spotify_service.get_seed_track_id(seed_track_info['seed_track']['artist'], seed_track_info['seed_track']['song'])
        if seed_track_id:
            diverse_tracks = spotify_service.get_audio_based_suggestions(seed_track_id, limit=9)
        else:
            logger.warning("Could not find seed track, using empty diverse tracks list")
            diverse_tracks = []
        
        # Extract data from responses
        genre = seed_track_info['music_genre']
        seed_track = seed_track_info['seed_track']
        suggested_playlist_name = seed_track_info['playlist_name']
        vibe_description = seed_track_info['vibe_description']
        
        # Use custom playlist name if provided, otherwise use AI suggestion
        final_playlist_name = playlist_name or suggested_playlist_name
        
        logger.info(f"🎵 GEMINI SEED TRACK ANALYSIS:")
        logger.info(f"   Genre: {genre}")
        logger.info(f"   Vibe: {vibe_description}")
        logger.info(f"   Seed Track: {seed_track['song']} by {seed_track['artist']}")
        logger.info(f"   Playlist Name: {final_playlist_name}")
        
        logger.info(f"🎵 SPOTIFY AUDIO-BASED SUGGESTIONS:")
        logger.info(f"   Generated {len(diverse_tracks)} diverse tracks")
        for i, track in enumerate(diverse_tracks, 1):
            # Get genres for this track
            track_genres = spotify_service.get_track_genres(track['track_id'])
            genres_str = ", ".join(track_genres) if track_genres else "No genres found"
            logger.info(f"   {i}. {track['song']} by {track['artist']} ({track['year']})")
            logger.info(f"      Genres: {genres_str}")
            logger.info(f"      Context: {track['context']}")
        
        # Get user information
        user = spotify_service.get_current_user()
        user_id = user['id']
        
        # Create playlist
        logger.info("Creating playlist with diverse track suggestions")
        playlist = spotify_service.sp.user_playlist_create(
            user=user_id, 
            name=final_playlist_name, 
            public=True
        )
        
        # Collect all track URIs to add
        track_uris = []
        found_tracks = 0
        
        # First, try to find the seed track
        seed_track_id = spotify_service.get_seed_track_id(seed_track['artist'], seed_track['song'])
        if seed_track_id:
            track_uris.append(f"spotify:track:{seed_track_id}")
            found_tracks += 1
            logger.info(f"✅ Found seed track: {seed_track['song']} by {seed_track['artist']}")
        else:
            logger.warning(f"❌ Could not find seed track: {seed_track['song']} by {seed_track['artist']}")
        
        # Then, add each diverse track (already found by Spotify's audio analysis)
        logger.info(f"Adding {len(diverse_tracks)} audio-based diverse tracks...")
        for i, track in enumerate(diverse_tracks, 1):
            try:
                track_uris.append(f"spotify:track:{track['track_id']}")
                found_tracks += 1
                logger.info(f"✅ {i}/{len(diverse_tracks)}: {track['song']} by {track['artist']} ({track['year']}) - {track['context']}")
            except Exception as e:
                logger.warning(f"❌ {i}/{len(diverse_tracks)}: Error adding {track['song']} by {track['artist']}: {e}")
        
        # Add all found tracks to the playlist
        if track_uris:
            # Add tracks in batches (Spotify has a limit of 100 tracks per request)
            batch_size = 100
            for i in range(0, len(track_uris), batch_size):
                batch = track_uris[i:i + batch_size]
                spotify_service.sp.playlist_add_items(playlist_id=playlist['id'], items=batch)
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} tracks")
            
            total_tracks = len(track_uris)
            logger.info(f"✅ Successfully added {total_tracks} tracks to playlist")
        else:
            logger.error("❌ No tracks found - playlist will be empty")
            total_tracks = 0
        
        # Upload cover image if available
        if thumbnail_data:
            try:
                spotify_service.upload_playlist_cover_image(playlist['id'], thumbnail_data)
            except Exception as e:
                logger.warning(f"Failed to upload cover image: {e}")
        
        logger.info(f"Created playlist: {playlist['external_urls']['spotify']}")
        
        return MusicRecommendationResponse(
            playlist_url=playlist['external_urls']['spotify'],
            playlist_name=final_playlist_name,
            tracks_added=total_tracks,
            seed_track={
                "name": seed_track['song'],
                "artist": seed_track['artist'],
                "id": seed_track_id if seed_track_id else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in recommend_music endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy")

@router.get("/debug/token")
async def debug_token(spotify_token: str):
    """Debug endpoint to check token scopes"""
    try:
        spotify_service = SpotifyService(user_token=spotify_token)
        user = spotify_service.get_current_user()
        
        # Try to get user's top tracks to test scopes
        try:
            top_tracks = spotify_service.get_user_top_tracks(limit=1)
            tracks_scope = "✅ user-top-read works"
        except Exception as e:
            tracks_scope = f"❌ user-top-read failed: {str(e)}"
        
        # Try to get recently played
        try:
            recent = spotify_service.get_user_recently_played(limit=1)
            recent_scope = "✅ user-read-recently-played works"
        except Exception as e:
            recent_scope = f"❌ user-read-recently-played failed: {str(e)}"
        
        return JSONResponse(content={
            "user": user['display_name'],
            "user_id": user['id'],
            "tracks_scope": tracks_scope,
            "recent_scope": recent_scope,
            "token_preview": spotify_token[:20] + "..."
        })
        
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/debug/spotify-connection")
async def debug_spotify_connection():
    """Debug endpoint to test Spotify API connection and genre retrieval"""
    try:
        from app.services.gemini import GeminiService
        gemini_service = GeminiService()
        genres = gemini_service._get_spotify_genres()
        
        return JSONResponse(content={
            "status": "✅ Spotify connection successful",
            "genres_count": len(genres),
            "sample_genres": genres[:10]  # First 10 genres
        })
    except Exception as e:
        return JSONResponse(content={
            "status": "❌ Spotify connection failed",
            "error": str(e)
        })

@router.get("/spotify/login")
async def spotify_login():
    """Initiate Spotify OAuth flow"""
    try:
        logger.info(f"Requesting scopes: {settings.SPOTIFY_SCOPE}")
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope=settings.SPOTIFY_SCOPE
        )
        
        auth_url = sp_oauth.get_authorize_url()
        logger.info(f"Auth URL: {auth_url}")
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Error initiating Spotify login: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate Spotify login")

@router.get("/spotify/callback")
async def spotify_callback(request: Request):
    """Handle Spotify OAuth callback - Step 2: Exchange code for token"""
    try:
        code = request.query_params.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not provided")
        
        # Step 2: Exchange authorization code for access token
        import httpx
        
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://accounts.spotify.com/api/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            token_info = response.json()
            access_token = token_info['access_token']
            expires_in = token_info.get('expires_in', 3600)
        
        # Step 3: Redirect to frontend with token
        frontend_callback_url = f"{settings.FRONTEND_URL}/spotify/callback"
        redirect_url = f"{frontend_callback_url}?access_token={access_token}&expires_in={expires_in}"
        
        logger.info(f"Successfully exchanged code for token, redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Error handling Spotify callback: {e}")
        # Redirect to frontend with error
        frontend_callback_url = f"{settings.FRONTEND_URL}/spotify/callback"
        error_url = f"{frontend_callback_url}?error=authentication_failed"
        return RedirectResponse(url=error_url)

@router.post("/spotify/callback")
async def spotify_callback_post(request: Request):
    """Handle Spotify OAuth callback from Postman - Step 2: Exchange code for token"""
    try:
        body = await request.json()
        code = body.get('code')
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not provided")
        
        # Step 2: Exchange authorization code for access token
        import httpx
        
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "client_secret": settings.SPOTIFY_CLIENT_SECRET
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://accounts.spotify.com/api/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            token_info = response.json()
        
        # Return token to frontend (in production, you might want to store this securely)
        return JSONResponse(content={
            "access_token": token_info['access_token'],
            "token_type": "Bearer",
            "expires_in": token_info.get('expires_in', 3600)
        })
        
    except Exception as e:
        logger.error(f"Error handling Spotify callback: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete Spotify authentication")
