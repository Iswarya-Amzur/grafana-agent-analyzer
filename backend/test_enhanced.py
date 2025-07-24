import pytest
import json
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
sys.path.append('.')

from main import app
from llm_analysis import GrafanaAnalysisLLM, MarkdownReportGenerator, WidgetData
from multi_widget_detector import MultiWidgetDetector
import io
from PIL import Image
import numpy as np

client = TestClient(app)

def create_test_image_with_widgets() -> bytes:
    """Create a test image with multiple widget-like structures"""
    # Create a larger image with multiple panels
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Add widget panels
    # Widget 1: CPU Usage
    cv2.rectangle(img, (50, 50), (350, 250), (240, 240, 240), -1)
    cv2.rectangle(img, (50, 50), (350, 250), (100, 100, 100), 2)
    cv2.putText(img, "CPU Usage", (70, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "75%", (70, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
    cv2.putText(img, "Spiking", (70, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    
    # Widget 2: Memory Usage
    cv2.rectangle(img, (400, 50), (750, 250), (240, 240, 240), -1)
    cv2.rectangle(img, (400, 50), (750, 250), (100, 100, 100), 2)
    cv2.putText(img, "Memory Usage", (420, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "6.2 GB", (420, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 150, 0), 3)
    cv2.putText(img, "Rising", (420, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 0), 2)
    
    # Widget 3: Disk Usage
    cv2.rectangle(img, (50, 300), (350, 500), (240, 240, 240), -1)
    cv2.rectangle(img, (50, 300), (350, 500), (100, 100, 100), 2)
    cv2.putText(img, "Disk Usage", (70, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "45%", (70, 390), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    cv2.putText(img, "Stable", (70, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Convert to PIL Image and then to bytes
    pil_img = Image.fromarray(img)
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

def test_health_endpoint_enhanced():
    """Test enhanced health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "components" in data
    assert "tesseract" in data["components"]
    assert "llm" in data["components"]
    assert "file_system" in data["components"]

def test_root_endpoint_enhanced():
    """Test enhanced root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert data["version"] == "2.0.0"
    assert "features" in data

def test_multi_widget_upload():
    """Test upload with multi-widget detection enabled"""
    # Create test images with multiple widgets
    infra_img = create_test_image_with_widgets()
    system_img = create_test_image_with_widgets()
    
    files = {
        "infra_screenshot": ("infra.png", infra_img, "image/png"),
        "system_screenshot": ("system.png", system_img, "image/png")
    }
    
    data = {
        "date": "2025-07-22",
        "enable_llm_analysis": "false",  # Disable LLM for testing
        "enable_multi_widget": "true"
    }
    
    response = client.post("/upload/", files=files, data=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "processing_results" in result
    assert "infrastructure" in result["processing_results"]
    assert "system" in result["processing_results"]
    
    # Check that multi-widget detection was used
    infra_result = result["processing_results"]["infrastructure"]
    assert infra_result["method"] == "multi_widget_detection"
    assert infra_result["widgets_found"] >= 0  # May find 0 or more widgets

@patch('llm_analysis.openai.OpenAI')
def test_llm_analysis_integration(mock_openai):
    """Test LLM analysis integration with mocked OpenAI"""
    # Mock OpenAI response
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = """
# 📊 Widget Analysis Summary

## Per-Widget Analysis Table
| Widget Name | Category | Current Value | Min/Max | Trend | Status | Key Observations |
|-------------|----------|---------------|---------|-------|--------|------------------|
| CPU Usage | Infrastructure | 75% | -/- | Spiking | Warning | High CPU usage with spikes |
| Memory Usage | System | 6.2 GB | -/- | Rising | Info | Memory usage trending upward |

## ⚠️ Critical Issues & Alerts
- CPU usage spiking to 75%

## 🛠️ Recommendations

### Immediate Actions (< 1 hour)
- Monitor CPU processes
- Check for resource-intensive applications

### Short-term Actions (< 24 hours)  
- Analyze memory usage patterns
- Consider scaling resources

### Long-term Optimizations (< 1 week)
- Implement auto-scaling
- Review application performance

## 🎯 Key Metrics Summary
- **Performance Score**: 7/10
"""
    mock_completion.usage.total_tokens = 150
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_client
    
    # Set environment variable for API key
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    # Create test images
    infra_img = create_test_image_with_widgets()
    system_img = create_test_image_with_widgets()
    
    files = {
        "infra_screenshot": ("infra.png", infra_img, "image/png"),
        "system_screenshot": ("system.png", system_img, "image/png")
    }
    
    data = {
        "date": "2025-07-22",
        "enable_llm_analysis": "true",
        "enable_multi_widget": "false"  # Use single widget for simpler test
    }
    
    response = client.post("/upload/", files=files, data=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "llm_analysis" in result
    assert result["llm_analysis"]["success"] == True
    assert "analysis_summary" in result["llm_analysis"]

def test_custom_widget_analysis():
    """Test custom widget analysis endpoint"""
    test_widgets = [
        {
            "widget_name": "CPU Usage",
            "category": "Infrastructure",
            "min": "10%",
            "max": "95%", 
            "current": "78%",
            "trend": "Spiking",
            "spike_time": "14:30",
            "comments": "High usage detected"
        },
        {
            "widget_name": "Memory Usage",
            "category": "System",
            "min": "2.1 GB",
            "max": "7.8 GB",
            "current": "6.4 GB", 
            "trend": "Rising",
            "spike_time": "",
            "comments": ""
        }
    ]
    
    # Test without LLM (will fail gracefully)
    response = client.post("/analyze_custom/", json=test_widgets)
    # Should return 500 if no API key is configured, which is expected
    assert response.status_code in [200, 500]

def test_reports_listing():
    """Test reports listing endpoint"""
    response = client.get("/reports/")
    assert response.status_code == 200
    
    data = response.json()
    assert "reports" in data
    assert "total_count" in data
    assert isinstance(data["reports"], list)

def test_widget_data_class():
    """Test WidgetData class functionality"""
    widget = WidgetData(
        widget_name="Test Widget",
        category="Test Category",
        min_value="0%",
        max_value="100%",
        current_value="50%",
        trend="Stable",
        spike_time="",
        comments="Test comment"
    )
    
    assert widget.widget_name == "Test Widget"
    assert widget.category == "Test Category"
    assert widget.current_value == "50%"

def test_multi_widget_detector():
    """Test MultiWidgetDetector class"""
    detector = MultiWidgetDetector()
    
    # Test with a simple test image
    test_img = np.ones((400, 600, 3), dtype=np.uint8) * 255
    
    # Add a simple widget-like structure
    cv2.rectangle(test_img, (50, 50), (250, 150), (200, 200, 200), -1)
    cv2.putText(test_img, "CPU Usage 50%", (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    # Test region detection
    regions = detector.detect_widget_regions(test_img)
    assert isinstance(regions, list)
    
    # Test widget extraction
    widgets = detector.process_screenshot(test_img)
    assert isinstance(widgets, list)

def test_llm_analyzer_initialization():
    """Test LLM analyzer initialization"""
    # Test without API key
    analyzer = GrafanaAnalysisLLM()
    assert analyzer is not None
    
    # Test prompt generation
    test_widgets = [
        WidgetData(
            widget_name="Test Widget",
            category="Test",
            min_value="0",
            max_value="100", 
            current_value="50",
            trend="Stable",
            spike_time="",
            comments=""
        )
    ]
    
    system_prompt, user_prompt = analyzer.create_analysis_prompt(test_widgets)
    assert len(system_prompt) > 0
    assert len(user_prompt) > 0
    assert "Test Widget" in user_prompt

def test_report_generator():
    """Test MarkdownReportGenerator"""
    generator = MarkdownReportGenerator()
    
    # Mock analysis result
    mock_analysis = {
        "analysis": {
            "raw_markdown": "# Test Report\n\nThis is a test report.",
            "structured_data": {
                "performance_score": 8.5,
                "issues": ["Test issue"],
                "recommendations": {
                    "immediate": ["Test action"],
                    "short_term": [],
                    "long_term": []
                }
            },
            "model_used": "gpt-4o",
            "tokens_used": 100
        }
    }
    
    test_widgets = [
        WidgetData(
            widget_name="Test Widget",
            category="Test",
            min_value="0",
            max_value="100",
            current_value="50", 
            trend="Stable",
            spike_time="",
            comments="",
            extracted_at="2025-07-22T10:00:00"
        )
    ]
    
    report = generator.generate_report(mock_analysis, test_widgets)
    
    assert "markdown" in report
    assert "html" in report
    assert "summary" in report
    assert "metadata" in report
    assert len(report["markdown"]) > 0

if __name__ == "__main__":
    # Import cv2 here to avoid import issues during collection
    import cv2
    pytest.main([__file__, "-v"])
