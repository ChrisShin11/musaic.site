#!/usr/bin/env python3
"""
Debug script to test Spotify genres API directly
"""

import os
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_direct_http_request():
    """Test Spotify genres API with direct HTTP requests"""
    try:
        print("🔍 Testing Spotify API with direct HTTP requests...")
        print("=" * 60)
        
        # Get credentials
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set")
            return False
        
        print("✅ Credentials found")
        
        # Step 1: Get access token using Client Credentials flow
        print("📡 Getting access token...")
        
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        token_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code != 200:
            print(f"❌ Failed to get access token. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        access_token = response.json().get("access_token")
        if not access_token:
            print("❌ No access token in response")
            return False
        
        print("✅ Access token obtained")
        
        # Step 2: Get available genre seeds
        print("📡 Getting available genre seeds...")
        
        genres_url = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(genres_url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            genres = data.get("genres", [])
            print(f"✅ Successfully retrieved {len(genres)} genres")
            
            # Show first 10 genres
            print("\nFirst 10 genres:")
            for i, genre in enumerate(genres[:10], 1):
                print(f"  {i:2d}. {genre}")
            
            if len(genres) > 10:
                print(f"  ... and {len(genres) - 10} more genres")
            
            return True
        else:
            print(f"❌ Failed to get genres. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_spotipy_version():
    """Test with different Spotipy approaches"""
    try:
        print("\n🔍 Testing Spotipy library...")
        print("=" * 60)
        
        import spotipy
        print(f"Spotipy version: {spotipy.__version__}")
        
        # Test 1: Client Credentials
        print("\nTesting Client Credentials flow...")
        from spotipy.oauth2 import SpotifyClientCredentials
        
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        try:
            # Try the method call
            data = sp.recommendation_genre_seeds()
            genres = data.get("genres", [])
            print(f"✅ Spotipy Client Credentials: {len(genres)} genres")
            return True
        except Exception as e:
            print(f"❌ Spotipy Client Credentials failed: {e}")
            
            # Try alternative method names
            print("\nTrying alternative method names...")
            try:
                data = sp.recommendation_genre_seeds()
                print("✅ recommendation_genre_seeds() worked")
                return True
            except Exception as e2:
                print(f"❌ recommendation_genre_seeds() failed: {e2}")
            
            try:
                data = sp.available_genre_seeds()
                print("✅ available_genre_seeds() worked")
                return True
            except Exception as e3:
                print(f"❌ available_genre_seeds() failed: {e3}")
            
            try:
                data = sp.genre_seeds()
                print("✅ genre_seeds() worked")
                return True
            except Exception as e4:
                print(f"❌ genre_seeds() failed: {e4}")
            
            return False
            
    except Exception as e:
        print(f"❌ Error testing Spotipy: {e}")
        return False

def main():
    """Main debug function"""
    print("🔍 Spotify Genres API Debug")
    print("=" * 80)
    
    # Test 1: Direct HTTP request
    success1 = test_direct_http_request()
    
    # Test 2: Spotipy library
    success2 = test_spotipy_version()
    
    print("\n" + "=" * 80)
    print("🔍 Debug Summary")
    print("=" * 80)
    
    if success1:
        print("✅ Direct HTTP request: SUCCESS")
    else:
        print("❌ Direct HTTP request: FAILED")
    
    if success2:
        print("✅ Spotipy library: SUCCESS")
    else:
        print("❌ Spotipy library: FAILED")
    
    if success1 and not success2:
        print("\n💡 Recommendation: Use direct HTTP requests instead of Spotipy")
    elif not success1 and not success2:
        print("\n💡 Recommendation: Check your Spotify app credentials and permissions")
    elif success1 and success2:
        print("\n💡 Both methods work - the issue might be elsewhere")

if __name__ == "__main__":
    main()
