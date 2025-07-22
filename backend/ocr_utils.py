import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
from typing import Dict, List, Tuple
import json

class AdvancedGrafanaOCR:
    """
    Advanced OCR processor with widget detection and layout analysis
    """
    
    def __init__(self):
        # Widget detection templates and patterns
        self.widget_patterns = {
            'cpu': ['cpu', 'processor', 'core'],
            'memory': ['memory', 'ram', 'mem'],
            'disk': ['disk', 'storage', 'io'],
            'network': ['network', 'traffic', 'bandwidth', 'eth'],
            'response_time': ['response', 'latency', 'time'],
            'throughput': ['throughput', 'requests', 'req/s', 'rps'],
            'error_rate': ['error', 'errors', 'failed', 'failure']
        }
    
    def detect_widget_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Detect individual widget regions in the screenshot
        """
        regions = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find contours to detect widget boundaries
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size to find widget-like regions
        min_area = 5000  # Minimum widget area
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                # Add some padding
                padding = 10
                regions.append({
                    'x': max(0, x - padding),
                    'y': max(0, y - padding),
                    'width': min(image.shape[1], w + 2*padding),
                    'height': min(image.shape[0], h + 2*padding),
                    'area': area
                })
        
        # Sort by area (largest first)
        regions.sort(key=lambda r: r['area'], reverse=True)
        
        return regions[:6]  # Return top 6 regions
    
    def extract_widget_type(self, text: str) -> str:
        """
        Classify widget type based on extracted text
        """
        text_lower = text.lower()
        
        for widget_type, patterns in self.widget_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return widget_type.replace('_', ' ').title()
        
        return "Unknown"
    
    def extract_metric_values(self, text: str) -> Dict[str, str]:
        """
        Extract various metric values from text using advanced patterns
        """
        values = {}
        
        # Percentage patterns
        percent_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
        
        # Memory/Storage patterns (KB, MB, GB, TB)
        memory_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(KB|MB|GB|TB)', text, re.IGNORECASE)
        
        # Time patterns (ms, s, m, h)
        time_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(ms|s|m|h)\b', text, re.IGNORECASE)
        
        # Rate patterns (req/s, ops/s, etc.)
        rate_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(req/s|rps|ops/s|tx/s|rx/s)', text, re.IGNORECASE)
        
        # Network patterns (Mbps, Gbps, etc.)
        network_matches = re.findall(r'(\d+(?:\.\d+)?)\s*(bps|Kbps|Mbps|Gbps)', text, re.IGNORECASE)
        
        # Process percentages
        if percent_matches:
            nums = [float(x) for x in percent_matches]
            values['current'] = f"{nums[-1]}%"
            if len(nums) > 1:
                values['min'] = f"{min(nums)}%"
                values['max'] = f"{max(nums)}%"
        
        # Process other units
        all_matches = memory_matches + time_matches + rate_matches + network_matches
        if all_matches:
            # Take the last match as current value
            last_match = all_matches[-1]
            values['current'] = f"{last_match[0]} {last_match[1]}"
        
        return values
    
    def detect_alert_status(self, text: str) -> str:
        """
        Detect alert status from text and colors
        """
        text_lower = text.lower()
        
        # Critical indicators
        critical_words = ['critical', 'alert', 'error', 'failed', 'down', 'offline']
        warning_words = ['warning', 'warn', 'high', 'elevated']
        ok_words = ['ok', 'normal', 'good', 'healthy', 'online']
        
        for word in critical_words:
            if word in text_lower:
                return "Critical"
        
        for word in warning_words:
            if word in text_lower:
                return "Warning"
        
        for word in ok_words:
            if word in text_lower:
                return "OK"
        
        return "Unknown"
    
    def extract_time_series_info(self, text: str) -> Dict[str, str]:
        """
        Extract time series related information
        """
        info = {}
        
        # Time range patterns
        time_range_pattern = r'last\s+(\d+)\s*(m|h|d|w)'
        time_range = re.search(time_range_pattern, text.lower())
        if time_range:
            info['time_range'] = f"{time_range.group(1)}{time_range.group(2)}"
        
        # Specific time patterns
        time_pattern = r'(\d{1,2}:\d{2}(?::\d{2})?)\s*(AM|PM)?'
        times = re.findall(time_pattern, text, re.IGNORECASE)
        if times:
            info['last_update'] = f"{times[-1][0]} {times[-1][1]}".strip()
        
        return info
    
    def process_widget_region(self, image: np.ndarray, region: Dict) -> Dict[str, any]:
        """
        Process a specific widget region
        """
        # Extract region
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        widget_img = image[y:y+h, x:x+w]
        
        # Preprocess for OCR
        processed = self.preprocess_for_ocr(widget_img)
        
        # Extract text
        text = pytesseract.image_to_string(processed, config='--psm 6')
        
        # Extract information
        widget_type = self.extract_widget_type(text)
        metric_values = self.extract_metric_values(text)
        alert_status = self.detect_alert_status(text)
        time_info = self.extract_time_series_info(text)
        
        return {
            'region': region,
            'widget_type': widget_type,
            'extracted_text': text.strip(),
            'values': metric_values,
            'alert_status': alert_status,
            'time_info': time_info
        }
    
    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Enhanced preprocessing for better OCR
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Resize if too small
        height, width = gray.shape
        if height < 100 or width < 100:
            scale_factor = max(100/height, 100/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh

# Test function
def test_ocr_processing():
    """
    Test function to validate OCR setup
    """
    try:
        # Test pytesseract installation
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {version}")
        
        # Create a simple test image with text
        test_img = np.ones((100, 300, 3), dtype=np.uint8) * 255
        cv2.putText(test_img, "CPU Usage: 75%", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        # Test OCR
        gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        print(f"OCR Test Result: {text.strip()}")
        
        return True
    except Exception as e:
        print(f"OCR Test Failed: {e}")
        return False

if __name__ == "__main__":
    test_ocr_processing()
