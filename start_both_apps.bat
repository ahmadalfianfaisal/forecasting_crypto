@echo off
REM Script untuk menjalankan aplikasi forecasting dan scheduler secara bersamaan di Windows

echo Starting Forecast Vibecoding Application and Scheduler...

REM Setup virtual environment
call venv\Scripts\activate.bat

REM Buka jendela baru untuk aplikasi utama
start "Forecast App" cmd /k "title Forecast App & python run_app.py"

REM Tunggu sebentar
timeout /t 3 /nobreak >nul

REM Buka jendela baru untuk scheduler
start "Model Scheduler" cmd /k "title Model Scheduler & python run_scheduler.py"

echo.
echo Applications started!
echo Forecast App is available at: http://localhost:8050
echo.
echo Two command prompt windows will open:
echo   - One for the main application
echo   - One for the model scheduler
echo.
echo Keep both windows open to maintain the services.
pause