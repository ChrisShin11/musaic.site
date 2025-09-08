#!/usr/bin/env python3
"""
Debug script to check what permissions a Spotify token has
"""

import requests
import json

def check_token_permissions(token):
    """Check what permissions a Spotify token has"""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 Checking Token Permissions...")
    print("=" * 60)
    
    # 1. Check user info
    print("1. Testing user info...")
    try:
        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User: {user_data.get('display_name', 'Unknown')} (ID: {user_data.get('id', 'Unknown')})")
            print(f"   Country: {user_data.get('country', 'Unknown')}")
            print(f"   Product: {user_data.get('product', 'Unknown')}")
        else:
            print(f"❌ User info failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ User info error: {e}")
    
    # 2. Check playlists
    print("\n2. Testing playlist access...")
    try:
        response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)
        if response.status_code == 200:
            playlists = response.json()
            print(f"✅ Can access playlists: {len(playlists.get('items', []))} playlists found")
        else:
            print(f"❌ Playlist access failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Playlist access error: {e}")
    
    # 3. Check recommendations with detailed error
    print("\n3. Testing recommendations API...")
    try:
        # Try with a known working track
        params = {
            'seed_tracks': '4iVbWcbOaZNWIiwcDlSfIm',  # Uptown Funk
            'limit': 3
        }
        response = requests.get('https://api.spotify.com/v1/recommendations', 
                              headers=headers, params=params)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Recommendations work: {len(data.get('tracks', []))} tracks found")
        else:
            print(f"❌ Recommendations failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
            # Check if it's a scope issue
            if response.status_code == 403:
                print("   💡 This looks like a scope/permission issue")
            elif response.status_code == 404:
                print("   💡 404 could mean:")
                print("      - Invalid track ID")
                print("      - Track not available in your market")
                print("      - API endpoint issue")
                print("      - Token scope issue")
                
    except Exception as e:
        print(f"❌ Recommendations error: {e}")
    
    # 4. Check audio features
    print("\n4. Testing audio features...")
    try:
        response = requests.get('https://api.spotify.com/v1/audio-features/4iVbWcbOaZNWIiwcDlSfIm', 
                              headers=headers)
        if response.status_code == 200:
            print("✅ Audio features work")
        else:
            print(f"❌ Audio features failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Audio features error: {e}")
    
    # 5. Check track info
    print("\n5. Testing track info...")
    try:
        response = requests.get('https://api.spotify.com/v1/tracks/4iVbWcbOaZNWIiwcDlSfIm', 
                              headers=headers)
        if response.status_code == 200:
            track_data = response.json()
            print(f"✅ Track info works: {track_data.get('name', 'Unknown')} by {track_data.get('artists', [{}])[0].get('name', 'Unknown')}")
            print(f"   Available markets: {len(track_data.get('available_markets', []))} markets")
        else:
            print(f"❌ Track info failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Track info error: {e}")

if __name__ == "__main__":
    print("🎵 Spotify Token Permission Debugger")
    print("=" * 60)
    
    token = input("Paste your Spotify token here: ").strip()
    
    if not token:
        print("❌ No token provided")
        exit(1)
    
    check_token_permissions(token)
    
    print("\n" + "=" * 60)
    print("💡 If recommendations are failing with 404, try:")
    print("   1. Get a fresh token with proper scopes")
    print("   2. Check if the track is available in your market")
    print("   3. Try with a different track ID")
    print("   4. Verify your Spotify app settings")
