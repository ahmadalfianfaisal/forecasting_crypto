@echo off
REM Script untuk setup awal di Windows

echo === Setup Forecast Vibecoding Application ===

REM Setup virtual environment jika belum ada
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Create data directories if they don't exist
if not exist "models" mkdir models
if not exist "mlruns" mkdir mlruns

echo Setup completed!
echo To start the application, run: python run_app.py
echo To start the scheduler, run: python run_scheduler.py
echo.
pause