@echo off
REM Grafana OCR Backend Setup Script for Windows

echo 🚀 Setting up Grafana OCR Backend...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is not installed. Please install pip first.
    pause
    exit /b 1
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

echo ✅ Backend setup complete!
echo.
echo 🔧 Next steps:
echo 1. Install Tesseract OCR:
echo    Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo    Add to PATH or update main.py with the installation path
echo.
echo 2. Start the server:
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
echo 3. Test the API:
echo    curl http://localhost:8000/health
echo.
pause
