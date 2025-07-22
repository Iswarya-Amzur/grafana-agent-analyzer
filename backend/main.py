from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import cv2
import numpy as np
import pytesseract
import re
from typing import List, Dict, Any, Optional
import io
from PIL import Image
import json
import os
from datetime import datetime
from pathlib import Path

# Import our new modules
from llm_analysis import GrafanaAnalysisLLM, MarkdownReportGenerator, WidgetData
from multi_widget_detector import MultiWidgetDetector, ExtractedWidget
from excel_export import ExcelReportGenerator

app = FastAPI(title="Grafana Screenshot OCR & LLM Analysis API", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create reports directory
REPORTS_DIR = Path("./reports")
REPORTS_DIR.mkdir(exist_ok=True)

class GrafanaOCR:
    def __init__(self):
        # Configure pytesseract if needed (uncomment and adjust path if required)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_with_confidence(self, image: np.ndarray) -> str:
        """Extract text using OCR with confidence scoring"""
        try:
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Filter out low confidence text
            text_parts = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Only include text with >30% confidence
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
            
            return ' '.join(text_parts)
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def extract_numeric_values(self, text: str) -> Dict[str, str]:
        """Extract numeric values and percentages from text"""
        values = {}
        
        # Pattern for percentages
        percent_pattern = r'(\d+(?:\.\d+)?)\s*%'
        percentages = re.findall(percent_pattern, text)
        
        # Pattern for numbers with units (KB, MB, GB, etc.)
        unit_pattern = r'(\d+(?:\.\d+)?)\s*(KB|MB|GB|TB|ms|s|m|h|req/s|ops/s)'
        units = re.findall(unit_pattern, text, re.IGNORECASE)
        
        # Pattern for plain numbers
        number_pattern = r'\b(\d+(?:\.\d+)?)\b'
        numbers = re.findall(number_pattern, text)
        
        # Try to identify min, max, current values
        if percentages:
            if len(percentages) >= 3:
                values['min'] = f"{min(map(float, percentages))}%"
                values['max'] = f"{max(map(float, percentages))}%"
                values['current'] = f"{percentages[-1]}%"
            elif len(percentages) == 1:
                values['current'] = f"{percentages[0]}%"
        
        if units:
            # Take the most recent unit value as current
            if units:
                values['current'] = f"{units[-1][0]} {units[-1][1]}"
        
        return values
    
    def detect_trends(self, text: str) -> str:
        """Detect trend indicators in the text"""
        text_lower = text.lower()
        
        # Trend keywords
        spike_indicators = ['spike', 'spiking', 'peak', 'surge', 'sudden increase']
        rising_indicators = ['rising', 'increasing', 'growing', 'up', 'higher']
        falling_indicators = ['falling', 'decreasing', 'dropping', 'down', 'lower']
        stable_indicators = ['stable', 'steady', 'constant', 'flat']
        
        for indicator in spike_indicators:
            if indicator in text_lower:
                return "Spiking"
        
        for indicator in rising_indicators:
            if indicator in text_lower:
                return "Rising"
        
        for indicator in falling_indicators:
            if indicator in text_lower:
                return "Falling"
        
        for indicator in stable_indicators:
            if indicator in text_lower:
                return "Stable"
        
        return "Unknown"
    
    def extract_time_info(self, text: str) -> str:
        """Extract time information from text"""
        # Pattern for time (HH:MM AM/PM)
        time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM)?)'
        times = re.findall(time_pattern, text, re.IGNORECASE)
        
        if times:
            return times[-1]  # Return the last found time
        
        return ""
    
    def extract_widget_title(self, text: str) -> str:
        """Extract likely widget title from text"""
        lines = text.split('\n')
        
        # Common Grafana widget titles
        common_titles = [
            'CPU Usage', 'Memory Usage', 'Disk Usage', 'Network Traffic',
            'Response Time', 'Throughput', 'Error Rate', 'Load Average',
            'Database Connections', 'Cache Hit Rate', 'Queue Length'
        ]
        
        # Look for exact matches first
        for line in lines:
            line_clean = line.strip()
            for title in common_titles:
                if title.lower() in line_clean.lower():
                    return title
        
        # If no exact match, return the first non-empty line that looks like a title
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) > 3 and len(line_clean) < 50 and not re.match(r'^\d', line_clean):
                return line_clean
        
        return "Unknown Widget"
    
    def process_screenshot(self, image_bytes: bytes, category: str) -> Dict[str, Any]:
        """Process a single screenshot and extract widget information"""
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_bytes))
            image_np = np.array(image)
            
            # Preprocess image
            processed = self.preprocess_image(image_np)
            
            # Extract text
            raw_text = self.extract_text_with_confidence(processed)
            
            # Extract structured information
            widget_title = self.extract_widget_title(raw_text)
            numeric_values = self.extract_numeric_values(raw_text)
            trend = self.detect_trends(raw_text)
            spike_time = self.extract_time_info(raw_text)
            
            return {
                "widget_name": widget_title,
                "category": category,
                "min": numeric_values.get("min", ""),
                "max": numeric_values.get("max", ""),
                "current": numeric_values.get("current", ""),
                "trend": trend,
                "spike_time": spike_time,
                "comments": "",
                "raw_text": raw_text,  # Include for debugging
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "widget_name": "Error",
                "category": category,
                "min": "",
                "max": "",
                "current": "",
                "trend": "Unknown",
                "spike_time": "",
                "comments": f"Processing error: {str(e)}",
                "raw_text": "",
                "extracted_at": datetime.now().isoformat()
            }

# Initialize processors
ocr_processor = GrafanaOCR()
multi_widget_detector = MultiWidgetDetector()
llm_analyzer = GrafanaAnalysisLLM()
report_generator = MarkdownReportGenerator()
excel_generator = ExcelReportGenerator()

@app.post("/upload/")
async def upload_screenshots(
    infra_screenshot: UploadFile = File(...),
    system_screenshot: UploadFile = File(...),
    date: str = Form(...),
    enable_llm_analysis: bool = Form(default=True),
    enable_multi_widget: bool = Form(default=True)
):
    """
    Upload and process Grafana screenshots to extract widget details with optional LLM analysis
    """
    try:
        # Validate file types
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        
        if infra_screenshot.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type for infrastructure screenshot")
        
        if system_screenshot.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type for system screenshot")
        
        # Read file contents
        infra_content = await infra_screenshot.read()
        system_content = await system_screenshot.read()
        
        # Process screenshots
        all_widgets = []
        processing_results = {}
        
        # Process infrastructure screenshot
        if enable_multi_widget:
            infra_image = np.array(Image.open(io.BytesIO(infra_content)))
            infra_widgets = multi_widget_detector.process_screenshot(infra_image, "Infrastructure")
            all_widgets.extend(infra_widgets)
            processing_results["infrastructure"] = {
                "method": "multi_widget_detection",
                "widgets_found": len(infra_widgets),
                "widgets": [asdict_widget(w) for w in infra_widgets]
            }
        else:
            # Fallback to single widget processing
            infra_result = ocr_processor.process_screenshot(infra_content, "Infrastructure")
            processing_results["infrastructure"] = {
                "method": "single_widget_ocr",
                "widgets_found": 1,
                "widgets": [infra_result]
            }
        
        # Process system screenshot
        if enable_multi_widget:
            system_image = np.array(Image.open(io.BytesIO(system_content)))
            system_widgets = multi_widget_detector.process_screenshot(system_image, "System")
            all_widgets.extend(system_widgets)
            processing_results["system"] = {
                "method": "multi_widget_detection",
                "widgets_found": len(system_widgets),
                "widgets": [asdict_widget(w) for w in system_widgets]
            }
        else:
            # Fallback to single widget processing
            system_result = ocr_processor.process_screenshot(system_content, "System")
            processing_results["system"] = {
                "method": "single_widget_ocr",
                "widgets_found": 1,
                "widgets": [system_result]
            }
        
        # Prepare response
        response = {
            "upload_date": date,
            "processed_at": datetime.now().isoformat(),
            "processing_results": processing_results,
            "summary": {
                "total_widgets": len(all_widgets),
                "widgets_with_trends": sum(1 for w in all_widgets if w.trend != "Unknown"),
                "widgets_with_spikes": sum(1 for w in all_widgets if "spike" in w.trend.lower())
            }
        }
        
        # Add LLM analysis if requested
        if enable_llm_analysis and all_widgets:
            try:
                # Convert ExtractedWidget objects to WidgetData for LLM
                widget_data_list = []
                for widget in all_widgets:
                    widget_data = WidgetData(
                        widget_name=widget.widget_name,
                        category=widget.category,
                        min_value=widget.min_value,
                        max_value=widget.max_value,
                        current_value=widget.current_value,
                        trend=widget.trend,
                        spike_time=widget.spike_time,
                        comments=widget.comments,
                        raw_ocr_text=widget.raw_text,
                        extracted_at=widget.extracted_at
                    )
                    widget_data_list.append(widget_data)
                
                # Perform LLM analysis
                analysis_result = llm_analyzer.analyze_widgets(widget_data_list)
                
                if analysis_result["success"]:
                    # Generate markdown report
                    report_data = report_generator.generate_report(analysis_result, widget_data_list)
                    
                    # Save report to file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    report_filename = f"grafana_analysis_{timestamp}.md"
                    report_path = REPORTS_DIR / report_filename
                    
                    with open(report_path, "w", encoding="utf-8") as f:
                        f.write(report_data["markdown"])
                    
                    # Generate Excel report
                    excel_file = None
                    try:
                        excel_file = excel_generator.generate_excel_report(analysis_result, widget_data_list)
                        excel_filename = os.path.basename(excel_file)
                    except Exception as e:
                        print(f"Excel generation failed: {e}")
                        excel_file = None
                    
                    response["llm_analysis"] = {
                        "success": True,
                        "analysis_summary": report_data["summary"],
                        "report_file": str(report_path),
                        "download_url": f"/download_report/{report_filename}",
                        "excel_file": excel_file,
                        "excel_download_url": f"/download_excel/{excel_filename}" if excel_file else None,
                        "structured_analysis": analysis_result["analysis"]["structured_data"],
                        "model_used": analysis_result["analysis"]["model_used"],
                        "tokens_used": analysis_result["analysis"]["tokens_used"]
                    }
                else:
                    response["llm_analysis"] = {
                        "success": False,
                        "error": analysis_result["error"],
                        "message": "LLM analysis failed - check API key configuration"
                    }
                    
            except Exception as e:
                response["llm_analysis"] = {
                    "success": False,
                    "error": str(e),
                    "message": "LLM analysis encountered an error"
                }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

def asdict_widget(widget: ExtractedWidget) -> Dict[str, Any]:
    """Convert ExtractedWidget to dictionary"""
    return {
        "widget_name": widget.widget_name,
        "category": widget.category,
        "min": widget.min_value,
        "max": widget.max_value,
        "current": widget.current_value,
        "trend": widget.trend,
        "spike_time": widget.spike_time,
        "comments": widget.comments,
        "confidence": widget.confidence,
        "raw_text": widget.raw_text,
        "extracted_at": widget.extracted_at
    }

@app.get("/download_report/{filename}")
async def download_report(filename: str):
    """Download a generated analysis report"""
    report_path = REPORTS_DIR / filename
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=str(report_path),
        filename=filename,
        media_type='text/markdown'
    )

@app.get("/download_excel/{filename}")
async def download_excel(filename: str):
    """Download a generated Excel report"""
    excel_path = REPORTS_DIR / filename
    
    if not excel_path.exists():
        raise HTTPException(status_code=404, detail="Excel file not found")
    
    return FileResponse(
        path=str(excel_path),
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.get("/reports/")
async def list_reports():
    """List all available analysis reports"""
    try:
        reports = []
        for report_file in REPORTS_DIR.glob("*.md"):
            stat = report_file.stat()
            reports.append({
                "filename": report_file.name,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "size_bytes": stat.st_size,
                "download_url": f"/download_report/{report_file.name}"
            })
        
        return {
            "reports": sorted(reports, key=lambda r: r["created_at"], reverse=True),
            "total_count": len(reports)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing reports: {str(e)}")

@app.post("/analyze_custom/")
async def analyze_custom_widgets(widget_data: List[Dict[str, Any]]):
    """
    Analyze custom widget data using LLM (for testing or external data)
    """
    try:
        # Convert input to WidgetData objects
        widget_data_list = []
        for data in widget_data:
            widget_data_obj = WidgetData(
                widget_name=data.get("widget_name", "Unknown"),
                category=data.get("category", "System"),
                min_value=data.get("min", ""),
                max_value=data.get("max", ""),
                current_value=data.get("current", ""),
                trend=data.get("trend", "Unknown"),
                spike_time=data.get("spike_time", ""),
                comments=data.get("comments", ""),
                raw_ocr_text=data.get("raw_text", ""),
                extracted_at=datetime.now().isoformat()
            )
            widget_data_list.append(widget_data_obj)
        
        # Perform LLM analysis
        analysis_result = llm_analyzer.analyze_widgets(widget_data_list)
        
        if analysis_result["success"]:
            # Generate report
            report_data = report_generator.generate_report(analysis_result, widget_data_list)
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"custom_analysis_{timestamp}.md"
            report_path = REPORTS_DIR / report_filename
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_data["markdown"])
            
            # Generate Excel report
            excel_file = None
            try:
                excel_file = excel_generator.generate_excel_report(analysis_result, widget_data_list)
                excel_filename = os.path.basename(excel_file)
            except Exception as e:
                print(f"Excel generation failed: {e}")
                excel_file = None
            
            return {
                "success": True,
                "analysis_summary": report_data["summary"],
                "report_file": str(report_path),
                "download_url": f"/download_report/{report_filename}",
                "excel_file": excel_file,
                "excel_download_url": f"/download_excel/{excel_filename}" if excel_file else None,
                "structured_analysis": analysis_result["analysis"]["structured_data"]
            }
        else:
            return {
                "success": False,
                "error": analysis_result["error"]
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "message": "Grafana Screenshot OCR & LLM Analysis API",
        "version": "2.0.0",
        "features": [
            "Multi-widget OCR detection",
            "LLM-powered analysis",
            "Markdown report generation",
            "Custom widget analysis"
        ],
        "endpoints": {
            "upload": "/upload/ - Upload screenshots for analysis",
            "reports": "/reports/ - List generated reports",
            "download": "/download_report/{filename} - Download report",
            "custom": "/analyze_custom/ - Analyze custom widget data"
        }
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Test OCR availability
        try:
            tesseract_version = pytesseract.get_tesseract_version()
            health_status["components"]["tesseract"] = {
                "status": "healthy",
                "version": str(tesseract_version)
            }
        except Exception as e:
            health_status["components"]["tesseract"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Test LLM availability (without making API call)
        try:
            llm_test = GrafanaAnalysisLLM()
            api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
            health_status["components"]["llm"] = {
                "status": "configured" if api_key_configured else "not_configured",
                "api_key_set": api_key_configured
            }
        except Exception as e:
            health_status["components"]["llm"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Test file system
        try:
            test_file = REPORTS_DIR / "health_check.tmp"
            test_file.write_text("test")
            test_file.unlink()
            health_status["components"]["file_system"] = {
                "status": "healthy",
                "reports_dir": str(REPORTS_DIR)
            }
        except Exception as e:
            health_status["components"]["file_system"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Health check failed"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
