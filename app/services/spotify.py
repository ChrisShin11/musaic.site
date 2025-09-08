import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.config import settings
from app.utils.logger import get_logger
from typing import Optional, List, Dict, Any

logger = get_logger(__name__)

class SpotifyService:
    def __init__(self, user_token: Optional[str] = None):
        """
        Initialize Spotify service with optional user token
        
        Args:
            user_token: User's Spotify access token (if provided, uses user auth)
        """
        if user_token:
            # Use user token for authentication
            self.sp = spotipy.Spotify(auth=user_token)
            self.is_user_auth = True
        else:
            # Use app authentication (client credentials)
            from spotipy.oauth2 import SpotifyClientCredentials
            auth_manager = SpotifyClientCredentials(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            self.is_user_auth = False
    
    def get_seed_track_id(self, artist_name: str, song_name: str) -> str | None:
        """Search for a track and return its ID"""
        try:
            logger.info(f"Searching for track: {artist_name} - {song_name}")
            query = f'artist:{artist_name} track:{song_name}'
            result = self.sp.search(q=query, type='track', limit=1)
            tracks = result['tracks']['items']
            
            if tracks:
                track_id = tracks[0]['id']
                logger.info(f"Found track ID: {track_id}")
                return track_id
            else:
                logger.warning(f"Track not found: {artist_name} - {song_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching for track: {e}")
            return None
    
    def get_track_genres(self, track_id: str) -> list[str]:
        """Get genres from a track's artists"""
        try:
            logger.info(f"Getting genres for track: {track_id}")
            
            # Get track details
            track_info = self.sp.track(track_id)
            genres = []
            
            # Get genres from all artists of the track
            for artist in track_info['artists']:
                artist_info = self.sp.artist(artist['id'])
                artist_genres = artist_info.get('genres', [])
                genres.extend(artist_genres)
                logger.info(f"Artist {artist['name']} genres: {artist_genres}")
            
            # Remove duplicates while preserving order
            unique_genres = list(dict.fromkeys(genres))
            logger.info(f"Track genres: {unique_genres}")
            
            return unique_genres
            
        except Exception as e:
            logger.error(f"Error getting track genres: {e}")
            return []
    
    def get_audio_based_suggestions(self, seed_track_id: str, limit: int = 9) -> list[dict]:
        """Get diverse track suggestions using Spotify's audio analysis and search"""
        try:
            logger.info(f"Getting audio-based suggestions for track: {seed_track_id}")
            
            # Get seed track info
            seed_track = self.sp.track(seed_track_id)
            seed_artist = seed_track['artists'][0]
            seed_genres = self.get_track_genres(seed_track_id)
            
            suggestions = []
            
            # Method 1: Get similar artists
            try:
                similar_artists = self.sp.artist_related_artists(seed_artist['id'])
                logger.info(f"Found {len(similar_artists['artists'])} similar artists")
                
                # Get top tracks from similar artists
                for artist in similar_artists['artists'][:3]:  # Top 3 similar artists
                    try:
                        top_tracks = self.sp.artist_top_tracks(artist['id'], country='US')
                        for track in top_tracks['tracks'][:2]:  # Top 2 tracks per artist
                            suggestions.append({
                                'song': track['name'],
                                'artist': track['artists'][0]['name'],
                                'year': int(track['album']['release_date'][:4]),
                                'context': f"Similar artist to {seed_artist['name']}",
                                'track_id': track['id']
                            })
                    except Exception as e:
                        logger.warning(f"Could not get top tracks for artist {artist['name']}: {e}")
            except Exception as e:
                logger.warning(f"Could not get similar artists: {e}")
            
            # Method 2: Search by genre and audio features
            if seed_genres:
                try:
                    # Get audio features of seed track
                    audio_features = self.sp.audio_features([seed_track_id])
                    if audio_features and audio_features[0]:
                        features = audio_features[0]
                        
                        # Search for tracks with similar audio characteristics
                        for genre in seed_genres[:2]:  # Use top 2 genres
                            try:
                                # Search by genre and filter by audio features
                                search_results = self.sp.search(
                                    q=f"genre:{genre}",
                                    type='track',
                                    limit=20
                                )
                                
                                # Filter by similar audio features
                                for track in search_results['tracks']['items']:
                                    if len(suggestions) >= limit:
                                        break
                                    
                                    # Check if track has similar audio features
                                    track_features = self.sp.audio_features([track['id']])
                                    if track_features and track_features[0]:
                                        tf = track_features[0]
                                        
                                        # Simple similarity check (within 0.2 range)
                                        if (abs(tf.get('danceability', 0) - features.get('danceability', 0)) < 0.2 and
                                            abs(tf.get('energy', 0) - features.get('energy', 0)) < 0.2 and
                                            abs(tf.get('valence', 0) - features.get('valence', 0)) < 0.2):
                                            
                                            suggestions.append({
                                                'song': track['name'],
                                                'artist': track['artists'][0]['name'],
                                                'year': int(track['album']['release_date'][:4]),
                                                'context': f"Similar audio features to {seed_track['name']}",
                                                'track_id': track['id']
                                            })
                            except Exception as e:
                                logger.warning(f"Could not search by genre {genre}: {e}")
                except Exception as e:
                    logger.warning(f"Could not get audio features: {e}")
            
            # Method 3: Search by year and popularity (for variety)
            try:
                seed_year = int(seed_track['album']['release_date'][:4])
                years_to_try = [seed_year - 10, seed_year - 5, seed_year + 5, seed_year + 10]
                
                for year in years_to_try:
                    if len(suggestions) >= limit:
                        break
                    
                    try:
                        search_results = self.sp.search(
                            q=f"year:{year}",
                            type='track',
                            limit=10
                        )
                        
                        for track in search_results['tracks']['items']:
                            if len(suggestions) >= limit:
                                break
                            
                            # Check if we already have this track
                            if not any(s['track_id'] == track['id'] for s in suggestions):
                                suggestions.append({
                                    'song': track['name'],
                                    'artist': track['artists'][0]['name'],
                                    'year': year,
                                    'context': f"Popular track from {year}",
                                    'track_id': track['id']
                                })
                    except Exception as e:
                        logger.warning(f"Could not search by year {year}: {e}")
            except Exception as e:
                logger.warning(f"Could not search by year: {e}")
            
            # Remove duplicates and limit results
            unique_suggestions = []
            seen_tracks = set()
            for suggestion in suggestions:
                if suggestion['track_id'] not in seen_tracks and len(unique_suggestions) < limit:
                    unique_suggestions.append(suggestion)
                    seen_tracks.add(suggestion['track_id'])
            
            logger.info(f"Generated {len(unique_suggestions)} audio-based suggestions")
            
            # Debug: Show the audio-based suggestions clearly with genres
            logger.info(f"🎵 SPOTIFY AUDIO-BASED SUGGESTIONS BREAKDOWN:")
            for i, suggestion in enumerate(unique_suggestions, 1):
                # Get genres for this track
                track_genres = self.get_track_genres(suggestion['track_id'])
                genres_str = ", ".join(track_genres) if track_genres else "No genres found"
                
                logger.info(f"   {i}. {suggestion['song']} by {suggestion['artist']} ({suggestion['year']})")
                logger.info(f"      Genres: {genres_str}")
                logger.info(f"      Context: {suggestion['context']}")
                logger.info(f"      Track ID: {suggestion['track_id']}")
            
            return unique_suggestions
            
        except Exception as e:
            logger.error(f"Error getting audio-based suggestions: {e}")
            return []
    
    def get_audio_features(self, track_id: str) -> dict | None:
        """Get audio features for a track"""
        try:
            logger.info(f"Getting audio features for track: {track_id}")
            audio_features = self.sp.audio_features([track_id])
            
            if audio_features and audio_features[0]:
                features = audio_features[0]
                return {
                    'acousticness': features['acousticness'],
                    'danceability': features['danceability'],
                    'energy': features['energy'],
                    'key': 'major' if features['mode'] == 1 else 'minor',
                    'valence': features['valence']
                }
            else:
                logger.warning(f"No audio features found for track: {track_id}")
                return None
                
        except Exception as e:
            logger.warning(f"Could not get audio features for track {track_id}: {e}")
            logger.info("This is normal for some tracks - audio features are not always available")
            return None
    
    def get_recommendations(self, seed_track_id: str, genre: str = None, limit: int = 10) -> list[str]:
        """Get music recommendations based on seed track and its actual genres"""
        try:
            logger.info(f"Getting recommendations for track: {seed_track_id}")
            
            # Get the track's actual genres from its artists
            track_genres = self.get_track_genres(seed_track_id)
            
            # Use track genres if available, otherwise fall back to provided genre
            if track_genres:
                # Use the first few genres from the track
                seed_genres = track_genres[:2]  # Spotify allows up to 5 seed genres
                logger.info(f"Using track genres: {seed_genres}")
            elif genre:
                seed_genres = [genre]
                logger.info(f"Using provided genre: {genre}")
            else:
                logger.warning("No genres available for recommendations")
                return []
            
            # Try to get audio features, but don't fail if unavailable
            audio_features = None
            try:
                audio_features = self.sp.audio_features([seed_track_id])
                if audio_features and audio_features[0]:
                    features = audio_features[0]
                    logger.info("Audio features available, using them for recommendations")
                    
                    # Debug prints for audio features
                    print(f"Acousticness of the seed track: {features['acousticness']}")
                    print(f"Danceability of the seed track: {features['danceability']}")
                    print(f"Energy of the seed track: {features['energy']}")
                    print(f"Key of the seed track: {'major' if features['mode'] == 1 else 'minor'}")
                    print(f"Valence of the seed track: {features['valence']}")
                else:
                    logger.warning("No audio features data returned")
            except Exception as e:
                logger.warning(f"Could not get audio features: {e}")
                logger.info("Proceeding with recommendations without audio features")

            # Get recommendations with or without audio features
            if audio_features and audio_features[0]:
                features = audio_features[0]
                # Use the features as targets for the recommendations
                recommendations = self.sp.recommendations(
                    seed_tracks=[seed_track_id],
                    seed_genres=seed_genres,
                    limit=limit,
                    target_acousticness=features['acousticness'],
                    target_danceability=features['danceability'],
                    target_energy=features['energy'],
                    target_valence=features['valence'],
                    target_mode=features['mode']
                )
            else:
                # Get recommendations without audio features
                logger.info("Getting recommendations without audio features")
                recommendations = self.sp.recommendations(
                    seed_tracks=[seed_track_id],
                    seed_genres=seed_genres,
                    limit=limit
                )
            
            track_uris = [track['uri'] for track in recommendations['tracks']]
            logger.info(f"Found {len(track_uris)} recommendations using genres: {seed_genres}")
            return track_uris
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            logger.info("Recommendations API failed, but track genre extraction worked")
            return []
    
    def create_playlist_with_recommendations(
        self, 
        user_id: str, 
        playlist_name: str, 
        seed_track_id: str, 
        genre: str, 
        thumbnail_data: str = None
    ) -> str:
        """Create a new playlist and add recommended tracks"""
        try:
            logger.info(f"Creating playlist: {playlist_name}")
            
            # Get song recommendations
            track_uris = self.get_recommendations(seed_track_id, genre)
            
            if not track_uris:
                raise ValueError("No recommendations found")
            
            # Create a new playlist
            playlist = self.sp.user_playlist_create(
                user=user_id, 
                name=playlist_name, 
                public=True
            )
            
            logger.info(f"Created playlist with ID: {playlist['id']}")
            
            # Add tracks to the playlist
            self.sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
            logger.info(f"Added {len(track_uris)} tracks to playlist")
            
            # Upload cover image if provided
            if thumbnail_data:
                try:
                    self.upload_playlist_cover_image(playlist['id'], thumbnail_data)
                    logger.info("Uploaded playlist cover image")
                except Exception as e:
                    logger.warning(f"Failed to upload cover image: {e}")
            
            return playlist['external_urls']['spotify']
            
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            raise
    
    def upload_playlist_cover_image(self, playlist_id: str, image_data: str) -> None:
        """Upload cover image for playlist"""
        try:
            logger.info(f"Uploading cover image for playlist: {playlist_id}")
            self.sp.playlist_upload_cover_image(
                playlist_id=playlist_id, 
                image_b64=image_data
            )
            logger.info("Cover image uploaded successfully")
        except Exception as e:
            logger.error(f"Error uploading cover image: {e}")
            raise
    
    def get_current_user(self) -> dict:
        """Get current user information"""
        try:
            return self.sp.current_user()
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise
    
    def get_user_top_tracks(self, time_range: str = 'medium_term', limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's top tracks"""
        try:
            logger.info(f"Getting user's top tracks for {time_range}")
            results = self.sp.current_user_top_tracks(time_range=time_range, limit=limit)
            return results['items']
        except Exception as e:
            logger.error(f"Error getting user's top tracks: {e}")
            return []
    
    def get_user_recently_played(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's recently played tracks"""
        try:
            logger.info(f"Getting user's recently played tracks")
            results = self.sp.current_user_recently_played(limit=limit)
            return [item['track'] for item in results['items']]
        except Exception as e:
            logger.error(f"Error getting recently played tracks: {e}")
            return []
    
    def get_user_top_artists(self, time_range: str = 'medium_term', limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's top artists"""
        try:
            logger.info(f"Getting user's top artists for {time_range}")
            results = self.sp.current_user_top_artists(time_range=time_range, limit=limit)
            return results['items']
        except Exception as e:
            logger.error(f"Error getting user's top artists: {e}")
            return []
    
    def get_user_genres(self) -> List[str]:
        """Get user's top genres from their top artists"""
        try:
            logger.info("Getting user's top genres")
            top_artists = self.get_user_top_artists(limit=20)
            genres = []
            for artist in top_artists:
                genres.extend(artist.get('genres', []))
            
            # Count genre frequency and return top ones
            from collections import Counter
            genre_counts = Counter(genres)
            return [genre for genre, count in genre_counts.most_common(5)]
        except Exception as e:
            logger.error(f"Error getting user genres: {e}")
            return []
    
    def get_smart_recommendations(
        self, 
        seed_track_id: str, 
        user_genres: List[str], 
        user_top_tracks: List[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[str]:
        """Get smart recommendations using user's music history"""
        try:
            logger.info("Getting smart recommendations based on user history")
            
            # Get audio features of the seed track
            audio_features = self.sp.audio_features([seed_track_id])
            if not audio_features or not audio_features[0]:
                logger.warning("No audio features available for recommendations")
                return []
            
            features = audio_features[0]
            
            # Use user's top genres if available, otherwise use provided genres
            if user_genres:
                seed_genres = user_genres[:2]  # Use top 2 genres
            else:
                seed_genres = ['pop']  # Fallback
            
            # Get additional seed tracks from user's top tracks
            seed_tracks = [seed_track_id]
            if user_top_tracks:
                # Add 1-2 more seed tracks from user's history
                additional_seeds = [track['id'] for track in user_top_tracks[:2] if track['id'] != seed_track_id]
                seed_tracks.extend(additional_seeds)
            
            # Limit to 5 seed tracks (Spotify's limit)
            seed_tracks = seed_tracks[:5]
            
            logger.info(f"Using seed tracks: {seed_tracks}")
            logger.info(f"Using seed genres: {seed_genres}")
            
            # Get recommendations
            recommendations = self.sp.recommendations(
                seed_tracks=seed_tracks,
                seed_genres=seed_genres,
                limit=limit,
                target_acousticness=features['acousticness'],
                target_danceability=features['danceability'],
                target_energy=features['energy'],
                target_valence=features['valence'],
                target_mode=features['mode']
            )
            
            track_uris = [track['uri'] for track in recommendations['tracks']]
            logger.info(f"Found {len(track_uris)} smart recommendations")
            return track_uris
            
        except Exception as e:
            logger.error(f"Error getting smart recommendations: {e}")
            return []
    
    def create_simple_playlist_with_recommendations(
        self, 
        user_id: str, 
        playlist_name: str, 
        seed_track_id: str, 
        genre: str
    ) -> str:
        """Create a simple playlist with recommendations (without cover image)"""
        try:
            logger.info(f"Creating simple playlist: {playlist_name}")
            
            # Get song recommendations
            track_uris = self.get_recommendations(seed_track_id, genre)
            
            if not track_uris:
                raise ValueError("No recommendations found")
            
            # Create a new playlist
            playlist = self.sp.user_playlist_create(
                user=user_id, 
                name=playlist_name, 
                public=True
            )
            
            logger.info(f"Created playlist with ID: {playlist['id']}")
            
            # Add tracks to the playlist
            self.sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
            logger.info(f"Added {len(track_uris)} tracks to playlist")
            
            return playlist['external_urls']['spotify']
            
        except Exception as e:
            logger.error(f"Error creating simple playlist: {e}")
            raise
