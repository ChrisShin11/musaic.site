# Musaic - AI Music Recommendation API

A FastAPI-based service that recommends music based on images using Google's Gemini AI and Spotify's API.

## Features

- 🖼️ **Image Analysis**: Uses Gemini AI to analyze uploaded images
- 🎵 **Music Recommendations**: Generates personalized playlists based on image content
- 🎧 **Spotify Integration**: Creates playlists directly in your Spotify account
- 🚀 **FastAPI**: Modern, fast web framework with automatic API documentation
- 📝 **Comprehensive Logging**: Structured logging with Loguru
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose

## Project Structure

```
fastapi-gemini-spotify/
│── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI entry point
│   ├── config.py        # Configuration settings
│   ├── routes.py        # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini.py    # Gemini AI service
│   │   └── spotify.py   # Spotify API service
│   └── utils/
│       ├── __init__.py
│       └── logger.py    # Logging configuration
│
│── tests/
│   ├── __init__.py
│   └── test_main.py     # Test cases
│
│── .env.example         # Environment variables template
│── .gitignore
│── requirements.txt     # Python dependencies
│── Dockerfile
│── docker-compose.yml
│── README.md
```

## Setup

### Prerequisites

- Python 3.12+
- Spotify Developer Account
- Google AI Studio Account (for Gemini API)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi-gemini-spotify
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the application**
   ```bash
   python -m app.main
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Spotify API Configuration
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8080/callback

# Logging Configuration
LOG_LEVEL=INFO
```

## API Usage

### Endpoints

- `POST /recommend_music/` - Upload an image to get personalized music recommendations
- `GET /spotify/login` - Initiate Spotify OAuth flow
- `GET /spotify/callback` - Handle Spotify OAuth callback
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)

### Authentication Flow

1. **Frontend initiates login**: Redirect user to `/spotify/login`
2. **User authorizes**: User logs in with Spotify and grants permissions
3. **Callback handling**: Spotify redirects to `/spotify/callback` with authorization code
4. **Token exchange**: Backend exchanges code for access token
5. **API usage**: Use access token in subsequent API calls

### Example Request

```bash
curl -X POST "http://localhost:8080/recommend_music/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_image.jpg" \
     -F "spotify_token=YOUR_SPOTIFY_ACCESS_TOKEN" \
     -F "playlist_name=My Custom Playlist"
```

### Example Response

```json
{
  "playlist_url": "https://open.spotify.com/playlist/your_playlist_id",
  "playlist_name": "When I'm feeling nostalgic",
  "tracks_added": 20,
  "seed_track": {
    "name": "Take My Breath",
    "artist": "The Weeknd",
    "id": "4iVbWcbOaZNWIiwcDlSfIm"
  }
}
```

### Frontend Integration

See `frontend_auth_example.html` for a complete example of how to integrate the authentication flow in your frontend application.

## Docker Deployment

### Using Docker Compose

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d
```

### Using Docker

```bash
# Build image
docker build -t musaic-api .

# Run container
docker run -p 8080:8080 --env-file .env musaic-api
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

- **`app/main.py`**: FastAPI application setup and configuration
- **`app/routes.py`**: API endpoint definitions
- **`app/config.py`**: Configuration management
- **`app/services/gemini.py`**: Gemini AI integration for image analysis
- **`app/services/spotify.py`**: Spotify API integration for playlist creation
- **`app/utils/logger.py`**: Logging configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.
