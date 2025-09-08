import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_recommend_music_no_file():
    """Test recommend music endpoint with no file"""
    response = client.post("/recommend_music/")
    assert response.status_code == 422  # FastAPI validation error

def test_recommend_music_invalid_file():
    """Test recommend music endpoint with invalid file type"""
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/recommend_music/", files=files)
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]
