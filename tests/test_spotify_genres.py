"""
Pytest tests for Spotify genres functionality
"""

import pytest
import os
from unittest.mock import Mock, patch
from app.services.spotify import SpotifyService
from app.services.gemini import GeminiService


class TestSpotifyGenres:
    """Test class for Spotify genres functionality"""
    
    def test_gemini_service_get_spotify_genres_success(self):
        """Test successful retrieval of Spotify genres from GeminiService"""
        # Test the method with our curated genres service
        gemini_service = GeminiService()
        genres = gemini_service._get_spotify_genres()
        
        # Assertions
        assert isinstance(genres, list)
        assert len(genres) > 0
        assert 'pop' in genres
        assert 'rock' in genres
        assert 'hip-hop' in genres
        assert 'electronic' in genres
    
    def test_spotify_genres_service_functionality(self):
        """Test SpotifyGenresService functionality"""
        from app.services.spotify_genres import SpotifyGenresService
        
        # Test getting available genres
        genres = SpotifyGenresService.get_available_genres()
        assert isinstance(genres, list)
        assert len(genres) > 0
        assert 'pop' in genres
        
        # Test genre validation
        assert SpotifyGenresService.is_valid_genre('pop') == True
        assert SpotifyGenresService.is_valid_genre('invalid-genre') == False
        
        # Test genre search
        rock_genres = SpotifyGenresService.search_genres('rock')
        assert isinstance(rock_genres, list)
        assert any('rock' in genre for genre in rock_genres)
        
        # Test popular genres
        popular = SpotifyGenresService.get_popular_genres()
        assert isinstance(popular, list)
        assert len(popular) > 0
        
        # Test genre categories
        categories = SpotifyGenresService.get_genres_by_category()
        assert isinstance(categories, dict)
        assert 'Rock' in categories
        assert 'Pop' in categories
    
    def test_spotify_service_get_user_genres_success(self):
        """Test successful retrieval of user genres from top artists"""
        # Mock user's top artists with genres
        mock_artists = [
            {'name': 'Artist 1', 'genres': ['pop', 'indie']},
            {'name': 'Artist 2', 'genres': ['rock', 'alternative']},
            {'name': 'Artist 3', 'genres': ['pop', 'electronic']},
            {'name': 'Artist 4', 'genres': ['hip-hop', 'rap']},
            {'name': 'Artist 5', 'genres': ['jazz', 'blues']}
        ]
        
        with patch.object(SpotifyService, 'get_user_top_artists', return_value=mock_artists):
            spotify_service = SpotifyService()
            user_genres = spotify_service.get_user_genres()
            
            # Should return top 5 most common genres
            assert len(user_genres) <= 5
            assert 'pop' in user_genres  # appears twice
            assert isinstance(user_genres, list)
    
    def test_spotify_service_get_user_genres_no_artists(self):
        """Test handling when user has no top artists"""
        with patch.object(SpotifyService, 'get_user_top_artists', return_value=[]):
            spotify_service = SpotifyService()
            user_genres = spotify_service.get_user_genres()
            
            assert user_genres == []
    
    def test_spotify_service_get_user_genres_api_error(self):
        """Test handling of API errors when getting user genres"""
        with patch.object(SpotifyService, 'get_user_top_artists', side_effect=Exception("API Error")):
            spotify_service = SpotifyService()
            user_genres = spotify_service.get_user_genres()
            
            assert user_genres == []
    
    def test_spotify_service_get_user_top_artists_success(self):
        """Test successful retrieval of user's top artists"""
        mock_artists = [
            {'name': 'Artist 1', 'genres': ['pop']},
            {'name': 'Artist 2', 'genres': ['rock']}
        ]
        mock_response = {'items': mock_artists}
        
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = Mock()
            mock_sp_instance.current_user_top_artists.return_value = mock_response
            mock_spotify.return_value = mock_sp_instance
            
            spotify_service = SpotifyService()
            artists = spotify_service.get_user_top_artists()
            
            assert artists == mock_artists
            assert len(artists) == 2
    
    def test_spotify_service_get_user_top_artists_api_error(self):
        """Test handling of API errors when getting top artists"""
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = Mock()
            mock_sp_instance.current_user_top_artists.side_effect = Exception("API Error")
            mock_spotify.return_value = mock_sp_instance
            
            spotify_service = SpotifyService()
            artists = spotify_service.get_user_top_artists()
            
            assert artists == []
    
    def test_spotify_service_get_user_top_tracks_success(self):
        """Test successful retrieval of user's top tracks"""
        mock_tracks = [
            {'name': 'Track 1', 'artists': [{'name': 'Artist 1'}]},
            {'name': 'Track 2', 'artists': [{'name': 'Artist 2'}]}
        ]
        mock_response = {'items': mock_tracks}
        
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = Mock()
            mock_sp_instance.current_user_top_tracks.return_value = mock_response
            mock_spotify.return_value = mock_sp_instance
            
            spotify_service = SpotifyService()
            tracks = spotify_service.get_user_top_tracks()
            
            assert tracks == mock_tracks
            assert len(tracks) == 2
    
    def test_spotify_service_get_user_top_tracks_api_error(self):
        """Test handling of API errors when getting top tracks"""
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = Mock()
            mock_sp_instance.current_user_top_tracks.side_effect = Exception("API Error")
            mock_spotify.return_value = mock_sp_instance
            
            spotify_service = SpotifyService()
            tracks = spotify_service.get_user_top_tracks()
            
            assert tracks == []
    
    def test_spotify_service_get_user_recently_played_success(self):
        """Test successful retrieval of user's recently played tracks"""
        mock_tracks = [
            {'track': {'name': 'Track 1', 'artists': [{'name': 'Artist 1'}]}},
            {'track': {'name': 'Track 2', 'artists': [{'name': 'Artist 2'}]}}
        ]
        mock_response = {'items': mock_tracks}
        
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = Mock()
            mock_sp_instance.current_user_recently_played.return_value = mock_response
            mock_spotify.return_value = mock_sp_instance
            
            spotify_service = SpotifyService()
            tracks = spotify_service.get_user_recently_played()
            
            expected_tracks = [item['track'] for item in mock_tracks]
            assert tracks == expected_tracks
            assert len(tracks) == 2
    
    def test_spotify_service_get_user_recently_played_api_error(self):
        """Test handling of API errors when getting recently played tracks"""
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = Mock()
            mock_sp_instance.current_user_recently_played.side_effect = Exception("API Error")
            mock_spotify.return_value = mock_sp_instance
            
            spotify_service = SpotifyService()
            tracks = spotify_service.get_user_recently_played()
            
            assert tracks == []
    
    def test_spotify_service_get_current_user_success(self):
        """Test successful retrieval of current user"""
        mock_user = {'id': 'user123', 'display_name': 'Test User'}
        
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = Mock()
            mock_sp_instance.current_user.return_value = mock_user
            mock_spotify.return_value = mock_sp_instance
            
            spotify_service = SpotifyService()
            user = spotify_service.get_current_user()
            
            assert user == mock_user
            assert user['id'] == 'user123'
            assert user['display_name'] == 'Test User'
    
    def test_spotify_service_get_current_user_api_error(self):
        """Test handling of API errors when getting current user"""
        with patch('spotipy.Spotify') as mock_spotify:
            mock_sp_instance = Mock()
            mock_sp_instance.current_user.side_effect = Exception("API Error")
            mock_spotify.return_value = mock_sp_instance
            
            spotify_service = SpotifyService()
            
            with pytest.raises(Exception, match="API Error"):
                spotify_service.get_current_user()


class TestSpotifyGenresIntegration:
    """Integration tests for Spotify genres functionality"""
    
    @pytest.mark.skipif(
        not os.getenv('SPOTIFY_CLIENT_ID') or not os.getenv('SPOTIFY_CLIENT_SECRET'),
        reason="Spotify credentials not available"
    )
    def test_real_spotify_genres_retrieval(self):
        """Test real Spotify genres retrieval (requires valid credentials)"""
        gemini_service = GeminiService()
        genres = gemini_service._get_spotify_genres()
        
        # Basic assertions
        assert isinstance(genres, list)
        assert len(genres) > 0
        
        # Check for common genres
        common_genres = ['pop', 'rock', 'hip-hop', 'electronic']
        found_common = [genre for genre in common_genres if genre in genres]
        assert len(found_common) > 0, f"Expected to find at least one common genre, found: {found_common}"
    
    @pytest.mark.skipif(
        not os.getenv('SPOTIFY_USER_TOKEN'),
        reason="Spotify user token not available"
    )
    def test_real_user_genres_retrieval(self):
        """Test real user genres retrieval (requires valid user token)"""
        user_token = os.getenv('SPOTIFY_USER_TOKEN')
        spotify_service = SpotifyService(user_token=user_token)
        
        # Test getting user info
        user = spotify_service.get_current_user()
        assert 'id' in user
        assert 'display_name' in user
        
        # Test getting user's top artists
        top_artists = spotify_service.get_user_top_artists(limit=5)
        assert isinstance(top_artists, list)
        
        # Test getting user's genres
        user_genres = spotify_service.get_user_genres()
        assert isinstance(user_genres, list)
        
        # Test getting user's top tracks
        top_tracks = spotify_service.get_user_top_tracks(limit=5)
        assert isinstance(top_tracks, list)
