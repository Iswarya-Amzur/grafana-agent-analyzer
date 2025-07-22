# Grafana Screenshot Uploader & OCR System

A complete solution for uploading Grafana screenshots and extracting widget details using OCR technology.

## 🏗️ Architecture

- **Frontend**: React.js + Tailwind CSS - Upload interface
- **Backend**: FastAPI + OpenCV + Pytesseract - OCR processing

## ✨ Features

### Frontend (React App)
- ✅ Upload two Grafana screenshots (Infrastructure & System)
- ✅ Optional date input (defaults to today's date)
- ✅ File preview with filename and size
- ✅ Loading indicators and upload feedback
- ✅ Responsive design with Grafana-inspired colors
- ✅ Form validation and error handling
- ✅ Modern UI with Tailwind CSS

### Backend (FastAPI OCR)
- 🔍 **OCR Text Extraction** using Pytesseract
- 🖼️ **Image Preprocessing** with OpenCV
- 📊 **Widget Detection** and classification
- 📈 **Trend Analysis** from text patterns
- 🕒 **Time Information** extraction
- 📋 **Structured JSON Output**

## 🚀 Quick Start

### Prerequisites
1. **Node.js 16+** for React frontend
2. **Python 3.8+** for FastAPI backend
3. **Tesseract OCR** - [Download here](https://github.com/tesseract-ocr/tesseract)

### Frontend Setup

```bash
# Install frontend dependencies
npm install

# Start React development server
npm start
```

Frontend runs on: `http://localhost:3000`

### Backend Setup

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Start FastAPI server
python main.py
```

Backend runs on: `http://localhost:8000`

## 📁 Project Structure

```
grafana-screenshot-uploader/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ScreenshotUploader.jsx    # Main upload component
│   │   ├── App.js                        # Main app component
│   │   ├── index.js                      # React entry point
│   │   └── index.css                     # Tailwind CSS imports
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
├── backend/
│   ├── main.py                           # FastAPI application
│   ├── ocr_utils.py                      # Advanced OCR utilities
│   ├── test_main.py                      # API tests
│   ├── requirements.txt                  # Python dependencies
│   ├── setup.bat                         # Windows setup script
│   └── setup.sh                          # Linux/Mac setup script
└── README.md                             # This file
```

## 🔄 Workflow

1. **Upload Screenshots**: User selects Infrastructure and System screenshots
2. **Send to Backend**: Frontend sends images via FormData to `/upload/`
3. **OCR Processing**: Backend processes images with OpenCV + Pytesseract
4. **Extract Data**: System extracts widget titles, values, trends
5. **Return Results**: Structured JSON with extracted information

## 📊 Example Output

```json
{
  "upload_date": "2025-07-22",
  "processed_at": "2025-07-22T10:30:00",
  "results": {
    "infrastructure": {
      "widget_name": "CPU Usage",
      "category": "Infrastructure",
      "min": "12%",
      "max": "98%",
      "current": "75%",
      "trend": "Spiking",
      "spike_time": "11:05 AM",
      "comments": ""
    },
    "system": {
      "widget_name": "Memory Usage",
      "category": "System",
      "min": "2.1 GB",
      "max": "7.8 GB", 
      "current": "6.2 GB",
      "trend": "Rising",
      "spike_time": "",
      "comments": ""
    }
  },
  "summary": {
    "total_widgets": 2,
    "widgets_with_trends": 2,
    "widgets_with_spikes": 1
  }
}
```

## 🛠️ Development

### Running Both Services

#### Option 1: VS Code Tasks
1. `Ctrl+Shift+P` → "Tasks: Run Task"
2. Select "Install Dependencies and Start Dev Server" (Frontend)
3. Select "Start OCR Backend Server" (Backend)

#### Option 2: Manual
```bash
# Terminal 1: Frontend
npm install && npm start

# Terminal 2: Backend  
cd backend && python main.py
```

### Testing

#### Frontend Testing
```bash
npm test
```

#### Backend Testing
```bash
cd backend
pytest test_main.py
```

#### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Upload test (with actual files)
curl -X POST "http://localhost:8000/upload/" \
  -F "infra_screenshot=@test_infra.png" \
  -F "system_screenshot=@test_system.png" \
  -F "date=2025-07-22"
```

## 🔧 Configuration

### Tesseract Path (Windows)
If Tesseract is not in PATH, update `backend/main.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Backend URL (Frontend)
Update API endpoint in `src/components/ScreenshotUploader.jsx`:

```javascript
const response = await fetch('http://localhost:8000/upload/', {
```

## 🎨 Customization

### Frontend Styling
- Modify Grafana colors in `tailwind.config.js`
- Update component styling in `ScreenshotUploader.jsx`
- Add new form fields as needed

### Backend OCR
- Adjust confidence threshold in `main.py`
- Modify preprocessing parameters in `ocr_utils.py`
- Add new widget detection patterns

## 🐛 Troubleshooting

### Common Issues

1. **"Tesseract not found"**
   - Install Tesseract OCR
   - Add to system PATH
   - Update `pytesseract.pytesseract.tesseract_cmd`

2. **CORS errors**
   - Check React app runs on `http://localhost:3000`
   - Verify CORS settings in `main.py`

3. **Poor OCR accuracy**
   - Use high-resolution screenshots
   - Ensure good contrast and quality
   - Adjust preprocessing parameters

## 📦 Technologies Used

### Frontend
- React.js 18
- Tailwind CSS 3
- Modern ES6+ JavaScript
- Responsive design principles

### Backend
- FastAPI - Web framework
- OpenCV - Image processing
- Pytesseract - OCR engine
- Pillow - Image handling
- NumPy - Numerical operations
- Uvicorn - ASGI server

## 📄 License

MIT License - Feel free to use this project for your Grafana monitoring needs!
