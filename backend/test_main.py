import pytest
import os
import json
from fastapi.testclient import TestClient
from main import app
import io
from PIL import Image
import numpy as np

client = TestClient(app)

def create_test_image_bytes(text: str = "CPU Usage: 75%") -> bytes:
    """Create a test image with text"""
    # Create white image
    img = Image.new('RGB', (300, 100), color='white')
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Grafana Screenshot OCR API"

def test_upload_endpoint_missing_files():
    """Test upload endpoint with missing files"""
    response = client.post("/upload/", data={"date": "2025-07-22"})
    assert response.status_code == 422  # Validation error

def test_upload_endpoint_success():
    """Test successful upload"""
    # Create test images
    infra_img = create_test_image_bytes("CPU Usage: 75%")
    system_img = create_test_image_bytes("Memory Usage: 4.2 GB")
    
    files = {
        "infra_screenshot": ("infra.png", infra_img, "image/png"),
        "system_screenshot": ("system.png", system_img, "image/png")
    }
    
    data = {"date": "2025-07-22"}
    
    response = client.post("/upload/", files=files, data=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "upload_date" in result
    assert "results" in result
    assert "infrastructure" in result["results"]
    assert "system" in result["results"]

def test_upload_invalid_file_type():
    """Test upload with invalid file type"""
    # Create a text file instead of image
    text_content = b"This is not an image"
    
    files = {
        "infra_screenshot": ("infra.txt", text_content, "text/plain"),
        "system_screenshot": ("system.png", create_test_image_bytes(), "image/png")
    }
    
    data = {"date": "2025-07-22"}
    
    response = client.post("/upload/", files=files, data=data)
    assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__])
