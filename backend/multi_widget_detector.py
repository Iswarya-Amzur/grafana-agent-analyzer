import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
from typing import Dict, List, Tuple, Any
import json
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class WidgetRegion:
    x: int
    y: int
    width: int
    height: int
    area: int
    confidence: float = 0.0

@dataclass
class ExtractedWidget:
    widget_name: str
    category: str
    min_value: str
    max_value: str
    current_value: str
    trend: str
    spike_time: str
    comments: str
    raw_text: str
    confidence: float
    region: WidgetRegion
    extracted_at: str

class MultiWidgetDetector:
    """
    Advanced widget detector for processing multiple widgets from Grafana screenshots
    """
    
    def __init__(self):
        # Widget classification patterns
        self.widget_categories = {
            'cpu': {
                'patterns': ['cpu', 'processor', 'core', 'cpu usage', 'cpu utilization'],
                'category': 'Infrastructure'
            },
            'memory': {
                'patterns': ['memory', 'ram', 'mem', 'memory usage', 'memory utilization'],
                'category': 'System'
            },
            'disk': {
                'patterns': ['disk', 'storage', 'disk usage', 'disk space', 'filesystem'],
                'category': 'Storage'
            },
            'network': {
                'patterns': ['network', 'bandwidth', 'eth', 'traffic', 'network traffic'],
                'category': 'Network'
            },
            'response_time': {
                'patterns': ['response', 'latency', 'response time', 'avg response'],
                'category': 'Performance'
            },
            'throughput': {
                'patterns': ['throughput', 'requests', 'req/s', 'rps', 'requests per second'],
                'category': 'Performance'
            },
            'error_rate': {
                'patterns': ['error', 'errors', 'error rate', 'failed', 'failure rate'],
                'category': 'Reliability'
            },
            'load': {
                'patterns': ['load', 'load average', 'system load', 'load avg'],
                'category': 'Infrastructure'
            },
            'database': {
                'patterns': ['database', 'db', 'connections', 'queries', 'sql'],
                'category': 'Database'
            },
            'cache': {
                'patterns': ['cache', 'hit rate', 'cache hit', 'redis', 'memcache'],
                'category': 'Performance'
            }
        }
        
        # Value extraction patterns
        self.value_patterns = {
            'percentage': r'(\d+(?:\.\d+)?)\s*%',
            'memory': r'(\d+(?:\.\d+)?)\s*(KB|MB|GB|TB)',
            'time': r'(\d+(?:\.\d+)?)\s*(ms|s|m|h)\b',
            'rate': r'(\d+(?:\.\d+)?)\s*(req/s|rps|ops/s|tx/s|rx/s)',
            'network': r'(\d+(?:\.\d+)?)\s*(bps|Kbps|Mbps|Gbps)',
            'number': r'\b(\d+(?:\.\d+)?)\b'
        }
        
        # Trend detection keywords
        self.trend_keywords = {
            'spiking': ['spike', 'spiking', 'peak', 'surge', 'sudden increase', 'sharp rise'],
            'rising': ['rising', 'increasing', 'growing', 'up', 'higher', 'climbing'],
            'falling': ['falling', 'decreasing', 'dropping', 'down', 'lower', 'declining'],
            'stable': ['stable', 'steady', 'constant', 'flat', 'normal'],
            'critical': ['critical', 'alert', 'danger', 'high', 'warning'],
            'normal': ['ok', 'good', 'healthy', 'normal', 'nominal']
        }
    
    def detect_widget_regions(self, image: np.ndarray, min_area: int = 3000) -> List[WidgetRegion]:
        """
        Detect multiple widget regions in a Grafana screenshot
        """
        regions = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply different detection methods
        regions.extend(self._detect_by_contours(gray, min_area))
        regions.extend(self._detect_by_panels(gray, min_area))
        regions.extend(self._detect_by_grid(gray, min_area))
        
        # Remove overlapping regions
        regions = self._remove_overlapping_regions(regions)
        
        # Sort by area (largest first)
        regions.sort(key=lambda r: r.area, reverse=True)
        
        return regions[:15]  # Return top 15 regions max
    
    def _detect_by_contours(self, gray: np.ndarray, min_area: int) -> List[WidgetRegion]:
        """Detect widgets using contour detection"""
        regions = []
        
        # Edge detection
        edges = cv2.Canny(gray, 30, 100)
        
        # Morphological operations to connect broken edges
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (typical for Grafana panels)
                aspect_ratio = w / h
                if 0.5 < aspect_ratio < 4.0:
                    regions.append(WidgetRegion(
                        x=max(0, x-10),
                        y=max(0, y-10),
                        width=w+20,
                        height=h+20,
                        area=area,
                        confidence=0.7
                    ))
        
        return regions
    
    def _detect_by_panels(self, gray: np.ndarray, min_area: int) -> List[WidgetRegion]:
        """Detect widgets by looking for panel-like structures"""
        regions = []
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Find rectangular structures
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                regions.append(WidgetRegion(
                    x=x, y=y, width=w, height=h, area=area, confidence=0.6
                ))
        
        return regions
    
    def _detect_by_grid(self, gray: np.ndarray, min_area: int) -> List[WidgetRegion]:
        """Detect widgets by assuming a grid layout"""
        regions = []
        h, w = gray.shape
        
        # Try different grid configurations common in Grafana
        grid_configs = [
            (2, 2), (3, 2), (2, 3), (3, 3), (4, 2), (2, 4), (4, 3), (3, 4)
        ]
        
        for rows, cols in grid_configs:
            cell_w = w // cols
            cell_h = h // rows
            
            if cell_w * cell_h > min_area:
                for r in range(rows):
                    for c in range(cols):
                        x = c * cell_w
                        y = r * cell_h
                        
                        # Add some overlap detection logic
                        regions.append(WidgetRegion(
                            x=x + 10, y=y + 10,
                            width=cell_w - 20, height=cell_h - 20,
                            area=cell_w * cell_h,
                            confidence=0.4
                        ))
        
        return regions
    
    def _remove_overlapping_regions(self, regions: List[WidgetRegion], overlap_threshold: float = 0.5) -> List[WidgetRegion]:
        """Remove overlapping regions, keeping the one with higher confidence"""
        filtered_regions = []
        
        for region in sorted(regions, key=lambda r: r.confidence, reverse=True):
            is_overlap = False
            
            for existing in filtered_regions:
                if self._calculate_overlap(region, existing) > overlap_threshold:
                    is_overlap = True
                    break
            
            if not is_overlap:
                filtered_regions.append(region)
        
        return filtered_regions
    
    def _calculate_overlap(self, region1: WidgetRegion, region2: WidgetRegion) -> float:
        """Calculate overlap ratio between two regions"""
        x1 = max(region1.x, region2.x)
        y1 = max(region1.y, region2.y)
        x2 = min(region1.x + region1.width, region2.x + region2.width)
        y2 = min(region1.y + region1.height, region2.y + region2.height)
        
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        area1 = region1.width * region1.height
        area2 = region2.width * region2.height
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def extract_widget_data(self, image: np.ndarray, region: WidgetRegion) -> ExtractedWidget:
        """Extract data from a specific widget region"""
        # Crop the region
        widget_img = image[region.y:region.y+region.height, region.x:region.x+region.width]
        
        # Preprocess for better OCR
        processed_img = self._preprocess_widget_image(widget_img)
        
        # Extract text using OCR
        raw_text = self._extract_text_with_confidence(processed_img)
        
        # Parse the extracted information
        widget_name = self._extract_widget_name(raw_text)
        category = self._classify_widget_category(raw_text, widget_name)
        values = self._extract_metric_values(raw_text)
        trend = self._detect_trend(raw_text)
        spike_time = self._extract_time_info(raw_text)
        
        return ExtractedWidget(
            widget_name=widget_name,
            category=category,
            min_value=values.get('min', ''),
            max_value=values.get('max', ''),
            current_value=values.get('current', ''),
            trend=trend,
            spike_time=spike_time,
            comments='',
            raw_text=raw_text,
            confidence=region.confidence,
            region=region,
            extracted_at=datetime.now().isoformat()
        )
    
    def _preprocess_widget_image(self, image: np.ndarray) -> np.ndarray:
        """Enhanced preprocessing for widget OCR"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Resize if too small
        h, w = gray.shape
        if h < 100 or w < 100:
            scale = max(100/h, 100/w, 2.0)
            new_w, new_h = int(w * scale), int(h * scale)
            gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh
    
    def _extract_text_with_confidence(self, image: np.ndarray) -> str:
        """Extract text with confidence filtering"""
        try:
            # Try different OCR configurations
            configs = [
                '--psm 6',  # Single block
                '--psm 8',  # Single word
                '--psm 13', # Raw line
                '--psm 11', # Sparse text
            ]
            
            best_text = ""
            best_confidence = 0
            
            for config in configs:
                try:
                    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                    
                    text_parts = []
                    total_conf = 0
                    valid_words = 0
                    
                    for i in range(len(data['text'])):
                        conf = int(data['conf'][i])
                        text = data['text'][i].strip()
                        
                        if conf > 30 and text:
                            text_parts.append(text)
                            total_conf += conf
                            valid_words += 1
                    
                    if valid_words > 0:
                        avg_conf = total_conf / valid_words
                        if avg_conf > best_confidence:
                            best_confidence = avg_conf
                            best_text = ' '.join(text_parts)
                
                except:
                    continue
            
            return best_text
            
        except Exception as e:
            return ""
    
    def _extract_widget_name(self, text: str) -> str:
        """Extract widget name/title"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Common Grafana widget titles
        known_titles = [
            'CPU Usage', 'CPU Utilization', 'Memory Usage', 'Memory Utilization',
            'Disk Usage', 'Disk Space', 'Network Traffic', 'Network I/O',
            'Response Time', 'Average Response Time', 'Throughput', 'Requests/sec',
            'Error Rate', 'Error Count', 'Load Average', 'System Load',
            'Database Connections', 'Cache Hit Rate', 'Queue Length',
            'Concurrent Users', 'Active Sessions', 'Bandwidth Usage'
        ]
        
        # Look for exact or partial matches
        for line in lines:
            for title in known_titles:
                if title.lower() in line.lower():
                    return title
        
        # If no match, try to identify from text patterns
        for line in lines:
            if len(line) > 3 and len(line) < 50:
                # Skip lines that start with numbers or symbols
                if not re.match(r'^[\d\%\$\-\+]', line):
                    # Check if it contains typical widget words
                    widget_words = ['usage', 'rate', 'time', 'count', 'average', 'total', 'load']
                    if any(word in line.lower() for word in widget_words):
                        return line
        
        # Fallback to first non-numeric line
        for line in lines:
            if not re.match(r'^\d+[\%\.\d]*', line) and len(line) > 2:
                return line
        
        return "Unknown Widget"
    
    def _classify_widget_category(self, text: str, widget_name: str) -> str:
        """Classify widget into categories"""
        text_lower = (text + " " + widget_name).lower()
        
        for widget_type, config in self.widget_categories.items():
            for pattern in config['patterns']:
                if pattern in text_lower:
                    return config['category']
        
        return "System"
    
    def _extract_metric_values(self, text: str) -> Dict[str, str]:
        """Extract numeric values from text"""
        values = {}
        
        # Extract all numeric values with units
        all_values = []
        
        for pattern_name, pattern in self.value_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        all_values.append(f"{match[0]} {match[1]}")
                    else:
                        all_values.append(match[0])
                else:
                    all_values.append(match)
        
        # Try to identify current, min, max values
        if all_values:
            if len(all_values) == 1:
                values['current'] = all_values[0]
            elif len(all_values) >= 3:
                # Try to parse numeric values for min/max detection
                numeric_values = []
                for val in all_values:
                    try:
                        num = float(re.search(r'(\d+(?:\.\d+)?)', str(val)).group(1))
                        numeric_values.append((num, val))
                    except:
                        continue
                
                if numeric_values:
                    numeric_values.sort(key=lambda x: x[0])
                    values['min'] = numeric_values[0][1]
                    values['max'] = numeric_values[-1][1]
                    values['current'] = all_values[-1]  # Assume last is current
            else:
                values['current'] = all_values[-1]
        
        return values
    
    def _detect_trend(self, text: str) -> str:
        """Detect trend from text"""
        text_lower = text.lower()
        
        for trend, keywords in self.trend_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return trend.title()
        
        return "Unknown"
    
    def _extract_time_info(self, text: str) -> str:
        """Extract time information"""
        time_patterns = [
            r'(\d{1,2}:\d{2}(?::\d{2})?)\s*(AM|PM)?',
            r'at\s+(\d{1,2}:\d{2})',
            r'(\d{1,2}:\d{2})'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return ' '.join(matches[0]) if isinstance(matches[0], tuple) else matches[0]
        
        return ""
    
    def process_screenshot(self, image: np.ndarray, category: str = "System") -> List[ExtractedWidget]:
        """Process a screenshot and extract all widgets"""
        widgets = []
        
        # Detect widget regions
        regions = self.detect_widget_regions(image)
        
        print(f"Detected {len(regions)} potential widget regions")
        
        # Extract data from each region
        for i, region in enumerate(regions):
            try:
                widget = self.extract_widget_data(image, region)
                # Only include widgets with meaningful data
                if widget.widget_name != "Unknown Widget" or widget.current_value:
                    widgets.append(widget)
                    print(f"Extracted widget {i+1}: {widget.widget_name}")
            except Exception as e:
                print(f"Error processing region {i+1}: {e}")
                continue
        
        return widgets

# Test function
def test_multi_widget_detection():
    """Test the multi-widget detector"""
    try:
        detector = MultiWidgetDetector()
        print("Multi-widget detector initialized")
        
        # Create a test image
        test_img = np.ones((600, 800, 3), dtype=np.uint8) * 255
        
        # Add some test "widgets"
        cv2.rectangle(test_img, (50, 50), (350, 250), (200, 200, 200), -1)
        cv2.putText(test_img, "CPU Usage", (70, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(test_img, "75%", (70, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
        
        cv2.rectangle(test_img, (400, 50), (750, 250), (200, 200, 200), -1)
        cv2.putText(test_img, "Memory Usage", (420, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(test_img, "6.2 GB", (420, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
        
        # Test widget detection
        regions = detector.detect_widget_regions(test_img)
        print(f"Detected {len(regions)} regions")
        
        # Test widget extraction
        widgets = detector.process_screenshot(test_img)
        print(f"Extracted {len(widgets)} widgets")
        
        for widget in widgets:
            print(f"- {widget.widget_name}: {widget.current_value}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    test_multi_widget_detection()
