#!/bin/bash

# Grafana OCR Backend Setup Script

echo "🚀 Setting up Grafana OCR Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Install Tesseract OCR:"
echo "   - Ubuntu/Debian: sudo apt-get install tesseract-ocr"
echo "   - macOS: brew install tesseract"
echo "   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
echo ""
echo "2. Start the server:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. Test the API:"
echo "   curl http://localhost:8000/health"
