# 🚀 Enhanced Grafana Screenshot OCR & LLM Analysis Backend

FastAPI backend service for extracting widget details from Grafana screenshots using OCR and analyzing them with AI-powered insights.

## ✨ Features

### 🔍 **Advanced OCR Processing**
- **Multi-widget Detection** - Automatically detects and processes multiple widgets per screenshot
- **Enhanced Image Preprocessing** with OpenCV for better accuracy
- **Confidence-based Text Extraction** using Pytesseract
- **37+ Widget Types Supported** - CPU, Memory, Disk, Network, Database, Performance metrics

### 🤖 **LLM-Powered Analysis**
- **GPT-4o Integration** for expert-level monitoring analysis
- **Custom Analysis Prompts** tailored for DevOps insights
- **Automated Issue Detection** with severity classifications
- **Actionable Recommendations** based on industry best practices

### 📊 **Comprehensive Reporting**
- **Markdown Reports** with structured analysis
- **HTML Export** for easy sharing
- **Executive Summaries** with key metrics
- **Performance Scoring** and trend analysis

### 🎯 **Advanced Capabilities**
- **Pattern Recognition** across multiple metrics
- **Correlation Analysis** between different widgets
- **Capacity Planning** insights
- **Alert Threshold Recommendations**

## 🏗️ Architecture

```
Backend Architecture:
├── main.py                     # FastAPI application with enhanced endpoints
├── llm_analysis.py            # LLM integration and analysis engine
├── multi_widget_detector.py   # Advanced OCR and widget detection
├── ocr_utils.py              # Enhanced OCR utilities
├── demo_llm_analysis.py      # Demo script with 37 sample widgets
└── reports/                   # Generated analysis reports
```

## 📋 API Endpoints

### 🔄 **Enhanced Upload Endpoint**
```
POST /upload/
```
**New Parameters:**
- `enable_llm_analysis` (bool): Enable AI analysis (default: true)
- `enable_multi_widget` (bool): Enable multi-widget detection (default: true)

**Enhanced Response:**
```json
{
  "upload_date": "2025-07-22",
  "processed_at": "2025-07-22T10:30:00",
  "processing_results": {
    "infrastructure": {
      "method": "multi_widget_detection",
      "widgets_found": 6,
      "widgets": [...]
    },
    "system": {
      "method": "multi_widget_detection", 
      "widgets_found": 8,
      "widgets": [...]
    }
  },
  "llm_analysis": {
    "success": true,
    "analysis_summary": "Performance Score: 7.5/10 | Critical Issues: 2 | Recommendations: 12",
    "report_file": "./reports/grafana_analysis_20250722_103000.md",
    "download_url": "/download_report/grafana_analysis_20250722_103000.md",
    "structured_analysis": {
      "performance_score": 7.5,
      "issues": ["CPU usage spiking to 85%", "Memory trend concerning"],
      "recommendations": {
        "immediate": ["Monitor CPU processes", "Check memory leaks"],
        "short_term": ["Scale resources", "Optimize queries"],
        "long_term": ["Implement auto-scaling", "Architecture review"]
      }
    },
    "model_used": "gpt-4o",
    "tokens_used": 2847
  }
}
```

### 📋 **Report Management**
```
GET /reports/                           # List all reports
GET /download_report/{filename}         # Download specific report
POST /analyze_custom/                   # Analyze custom widget data
```

### 🔍 **Enhanced Health Check**
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "components": {
    "tesseract": {"status": "healthy", "version": "5.3.0"},
    "llm": {"status": "configured", "api_key_set": true},
    "file_system": {"status": "healthy", "reports_dir": "./reports"}
  }
}
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start Server
```bash
python main.py
```

### 4. Test with Demo Data
```bash
# Generate 37 sample widgets and analyze with LLM
python demo_llm_analysis.py --api-key YOUR_API_KEY --widget-count 37
```

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4000

# OCR Settings
OCR_CONFIDENCE_THRESHOLD=30
OCR_MIN_WIDGET_AREA=3000

# Report Settings
REPORT_OUTPUT_DIR=./reports
ENABLE_HTML_REPORTS=true
ENABLE_JSON_EXPORT=true
```

### Widget Detection Tuning
```python
# Adjust in multi_widget_detector.py
min_area = 3000              # Minimum widget area in pixels
confidence_threshold = 0.5   # Widget detection confidence
overlap_threshold = 0.5      # Overlap removal threshold
```

## 🎯 LLM Analysis Features

### 📊 **Comprehensive Analysis**
- **37+ Widget Types** automatically classified
- **Performance Scoring** (0-10 scale)
- **Trend Analysis** with pattern recognition
- **Issue Prioritization** (Critical/Warning/Info)

### 🔍 **Expert-Level Insights**
```markdown
# Generated Analysis Example:

## 🚨 Executive Summary
**Overall System Health**: Fair
**Priority Issues**: 3
**Immediate Actions Required**: Yes

## Infrastructure Health Matrix
| Component | Status | Current Load | Trend | Risk Level | Action Needed |
|-----------|--------|--------------|-------|------------|---------------|
| CPU | 🔴 | 85% | ↗️ | High | Scale immediately |
| Memory | 🟡 | 72% | ↗️ | Medium | Monitor closely |
| Storage | 🟢 | 45% | ➡️ | Low | Normal operation |

## ⚠️ Critical Issues Requiring Immediate Attention
### 🔴 Severity 1 (Fix within 1 hour)
- CPU usage consistently above 80% with spiking pattern
- Database query response time exceeding 1000ms

### 🟡 Severity 2 (Fix within 24 hours)  
- Memory usage trending upward, approaching 80% threshold
- Error rate increased to 2.3% (above 2% SLA)
```

## 🧪 Testing

### Run Enhanced Tests
```bash
# Run all tests
python -m pytest test_enhanced.py -v

# Test specific components
python -m pytest test_enhanced.py::test_llm_analysis_integration -v
python -m pytest test_enhanced.py::test_multi_widget_upload -v
```

### Demo Analysis
```bash
# Run demo with sample data
python demo_llm_analysis.py --widget-count 37 --api-key YOUR_KEY

# Output includes:
# - Generated widget data (JSON)
# - LLM analysis report (Markdown)
# - HTML report for sharing
# - Analysis metadata
```

## 📈 Sample Widget Data

The system supports analysis of 37+ widget types:

### **Infrastructure (8 widgets)**
- CPU Usage, CPU Load Average, Memory Usage, Memory Available
- Disk Usage /, Disk Usage /var, Disk I/O Read, Disk I/O Write

### **Network (4 widgets)**  
- Network In/Out, Network Errors, TCP Connections

### **Performance (6 widgets)**
- Response Time, Throughput, Error Rate, Success Rate, Cache Hit Rate, API Latency

### **Database (4 widgets)**
- DB Connections, Query Time, Lock Waits, Cache Hit Rate

### **Application (7 widgets)**
- Active Users, Sessions, Queue Length, Upload Rate, Processing Queue, Concurrent Tasks, Worker Threads

### **Container/K8s (4 widgets)**
- Pod CPU/Memory Usage, Container Restarts, Node Count

### **Observability (4 widgets)**
- Log Errors, Alert Count, Backup Status, SSL Cert Expiry

## 🔧 Advanced Usage

### Custom Analysis Prompts
```python
# Customize analysis in llm_analysis.py
system_prompt = """
You are a Senior DevOps Engineer analyzing Grafana metrics...
[Custom prompt for specific use cases]
"""
```

### Multi-Widget Detection Tuning
```python
# Adjust detection parameters
detector = MultiWidgetDetector()
detector.widget_categories['custom'] = {
    'patterns': ['custom_metric', 'special_widget'],
    'category': 'Custom'
}
```

### Report Customization
```python
# Modify report template in llm_analysis.py
report_template = """
# Custom Report Template
{{ analysis_content }}
[Add custom sections]
"""
```

## 🐛 Troubleshooting

### Common Issues

1. **LLM Analysis Fails**
   ```bash
   # Check API key configuration
   echo $OPENAI_API_KEY
   
   # Test API connectivity
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

2. **Poor OCR Accuracy**
   ```python
   # Adjust preprocessing parameters
   cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
   ```

3. **Widget Detection Issues**
   ```python
   # Lower detection threshold
   min_area = 2000  # Reduce from 3000
   confidence_threshold = 0.3  # Reduce from 0.5
   ```

## 📊 Performance Metrics

- **OCR Processing**: ~2-5 seconds per screenshot
- **LLM Analysis**: ~10-30 seconds for 37 widgets
- **Report Generation**: ~1-2 seconds
- **Total Processing**: ~15-40 seconds end-to-end

## 🔮 Roadmap

- [ ] **Real-time Analysis** - WebSocket streaming
- [ ] **Custom Models** - Fine-tuned for specific environments  
- [ ] **Trend Prediction** - ML-based forecasting
- [ ] **Integration APIs** - Direct Grafana plugin
- [ ] **Team Collaboration** - Shared analysis workspace

## 📄 Dependencies

**Core Requirements:**
- FastAPI 0.104.1 - Web framework
- OpenAI 1.13.3 - LLM integration
- OpenCV 4.8.1 - Image processing
- Pytesseract 0.3.10 - OCR engine

**LLM & Analysis:**
- LangChain 0.1.10 - LLM framework
- Jinja2 3.1.3 - Template engine
- Markdown 3.5.2 - Report formatting

**Complete list:** See `requirements.txt`

---

🔗 **API Documentation**: http://localhost:8000/docs  
📊 **Health Check**: http://localhost:8000/health  
📋 **Reports**: http://localhost:8000/reports/
