import json
import base64
from io import BytesIO
from PIL import Image
import google.generativeai as genai
import spotipy
from app.config import settings
from app.utils.logger import get_logger
from app.models import GeminiMusicRecommendation

logger = get_logger(__name__)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def resize_image(self, image: Image.Image, target_size: tuple = None) -> Image.Image:
        """Resize the image to target size"""
        if target_size is None:
            target_size = settings.IMAGE_TARGET_SIZE
        
        logger.info(f"Resizing image to {target_size}")
        return image.resize(target_size, Image.Resampling.LANCZOS)
    
    def compress_image(self, image: Image.Image, max_size_kb: int = None) -> BytesIO:
        """Compress image by reducing quality"""
        if max_size_kb is None:
            max_size_kb = settings.IMAGE_MAX_SIZE_KB
        
        logger.info(f"Compressing image to max {max_size_kb}KB")
        buffered = BytesIO()
        quality = settings.IMAGE_QUALITY
        image.save(buffered, format="JPEG", quality=quality)
        
        while buffered.tell() > max_size_kb * 1024 and quality > 10:
            quality -= 5
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=quality)
        
        logger.info(f"Image compressed to {buffered.tell() / 1024:.2f}KB with quality {quality}")
        return buffered
    
    def process_image(self, image: Image.Image) -> tuple[str, str]:
        """Process image and return both full and compressed base64 data"""
        # Convert RGBA to RGB if necessary (fixes JPEG conversion error)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert image to base64 (full size)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        
        # Create compressed thumbnail
        thumbnail = self.resize_image(image)
        buffered_thumbnail = self.compress_image(thumbnail)
        thumbnail_data = base64.b64encode(buffered_thumbnail.getvalue()).decode("utf-8")
        
        return image_data, thumbnail_data
    
    def analyze_image_for_seed_track(self, image_data: str) -> dict:
        """Step 1: Analyze image and suggest one perfect seed track"""
        try:
            logger.info("Step 1: Analyzing image for seed track with Gemini")
            
            # Get available Spotify genres
            available_genres = self._get_spotify_genres()
            
            prompt = f"""You are a music assistant that finds the perfect song for an image. 
            Analyze the image and return a JSON object with:
            
            1. 'seed_track': A single song that fits the image perfectly
               - 'song': Song title
               - 'artist': Artist name
            2. 'playlist_name': A creative playlist name starting with 'When...'
            3. 'music_genre': The primary genre that matches the image
            4. 'vibe_description': A brief description of the overall vibe/mood
            
            Choose a well-known, popular song that perfectly captures the image's mood and theme.
            
            Available genres: {', '.join(available_genres[:50])}
            
            Return only the JSON object, no extra text."""
            
            # Create the image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }
            
            # Generate content with Gemini
            response = self.model.generate_content([prompt, image_part])
            
            # Extract JSON from response
            response_text = response.text.strip()
            logger.info(f"Step 1 Gemini response: {response_text}")
            
            # Find JSON in response
            start_index = response_text.find("{")
            end_index = response_text.rfind("}") + 1
            
            if start_index == -1 or end_index == -1:
                raise ValueError("No JSON found in Gemini response")
            
            json_string = response_text[start_index:end_index]
            response_json = json.loads(json_string)
            
            logger.info(f"Step 1 parsed: {response_json}")
            
            # Debug: Show the seed track recommendation clearly
            logger.info(f"🎯 GEMINI SEED TRACK RECOMMENDATION:")
            logger.info(f"   Song: {response_json.get('seed_track', {}).get('song', 'N/A')}")
            logger.info(f"   Artist: {response_json.get('seed_track', {}).get('artist', 'N/A')}")
            logger.info(f"   Genre: {response_json.get('music_genre', 'N/A')}")
            logger.info(f"   Vibe: {response_json.get('vibe_description', 'N/A')}")
            
            return response_json
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from Gemini response: {e}")
            raise ValueError(f"Failed to decode JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error analyzing image with Gemini: {e}")
            raise

    def generate_diverse_tracks(self, seed_track_info: dict, image_data: str) -> list:
        """Step 2: Generate 9 diverse tracks based on seed track and image"""
        try:
            logger.info("Step 2: Generating diverse tracks with Gemini")
            
            # Get available Spotify genres
            available_genres = self._get_spotify_genres()
            
            prompt = f"""You are a music curator creating a diverse playlist. 
            Based on the seed track and image context, generate 9 additional tracks that:
            
            - Keep the same genre and overall vibe as the seed track
            - Include variety in artists (mix of popular and lesser-known)
            - Span different decades (from old classics to modern hits)
            - Include 1-2 tracks that are contextually fitting to the image theme
            - Maintain the same mood and energy level
            
            Seed track: {seed_track_info['seed_track']['song']} by {seed_track_info['seed_track']['artist']}
            Genre: {seed_track_info['music_genre']}
            Vibe: {seed_track_info['vibe_description']}
            
            Return a JSON array of 9 tracks, each with:
            - 'song': Song title
            - 'artist': Artist name  
            - 'year': Release year (approximate)
            - 'context': Why this song fits the vibe and image theme
            
            Available genres: {', '.join(available_genres[:50])}
            
            Return only the JSON array, no extra text."""
            
            # Create the image part for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }
            
            # Generate content with Gemini
            response = self.model.generate_content([prompt, image_part])
            
            # Extract JSON from response
            response_text = response.text.strip()
            logger.info(f"Step 2 Gemini response: {response_text}")
            
            # Find JSON array in response
            start_index = response_text.find("[")
            end_index = response_text.rfind("]") + 1
            
            if start_index == -1 or end_index == -1:
                raise ValueError("No JSON array found in Gemini response")
            
            json_string = response_text[start_index:end_index]
            diverse_tracks = json.loads(json_string)
            
            logger.info(f"Step 2 generated {len(diverse_tracks)} diverse tracks")
            return diverse_tracks
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from Gemini response: {e}")
            raise ValueError(f"Failed to decode JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating diverse tracks with Gemini: {e}")
            raise
    
    def _get_spotify_genres(self) -> list[str]:
        """Get available Spotify genres using our curated list."""
        try:
            from app.services.spotify_genres import SpotifyGenresService
            genres = SpotifyGenresService.get_available_genres()
            logger.info(f"Retrieved {len(genres)} valid Spotify genres from curated list")
            return genres

        except Exception as e:
            logger.error(f"Failed to retrieve Spotify genres: {e}")
            raise ValueError(f"Failed to retrieve Spotify genres: {e}")
