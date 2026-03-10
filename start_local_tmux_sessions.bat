@echo off
REM Script untuk setup dan menjalankan aplikasi forecasting secara lokal dengan tmux di Windows

REM Nama session tmux
set APP_SESSION=forecast-app-local
set SCHEDULER_SESSION=model-scheduler-local

echo Setting up local tmux sessions for forecast application...

REM Cek apakah tmux sudah terinstall (memerlukan WSL atau Cygwin)
where tmux >nul 2>nul
if errorlevel 1 (
    echo Installing tmux through WSL...
    echo Please install WSL first if not already installed
    wsl --install -d Ubuntu
    wsl bash -c "sudo apt update && sudo apt install -y tmux"
) else (
    echo tmux is already installed
)

REM Setup virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Buat session tmux untuk aplikasi utama
echo Creating tmux session for main application: %APP_SESSION%
wsl tmux new-session -d -s %APP_SESSION%

REM Kirim perintah ke session aplikasi
wsl tmux send-keys -t %APP_SESSION% "cd /mnt/c/Users/admin/alibaba-cloud/forecast-vibecoding && source venv/bin/activate && python run_app.py" Enter

echo Application started in tmux session: %APP_SESSION%
echo Access via: wsl tmux attach -t %APP_SESSION%
echo Or access via web browser: http://localhost:8050

REM Buat session tmux untuk scheduler
echo Creating tmux session for model scheduler: %SCHEDULER_SESSION%
wsl tmux new-session -d -s %SCHEDULER_SESSION%

REM Kirim perintah ke session scheduler
wsl tmux send-keys -t %SCHEDULER_SESSION% "cd /mnt/c/Users/admin/alibaba-cloud/forecast-vibecoding && source venv/bin/activate && python run_scheduler.py" Enter

echo Scheduler started in tmux session: %SCHEDULER_SESSION%
echo Access via: wsl tmux attach -t %SCHEDULER_SESSION%

echo.
echo Both sessions are now running in the background!
echo.
echo To view sessions: wsl tmux ls
echo To attach to app: wsl tmux attach -t %APP_SESSION%
echo To attach to scheduler: wsl tmux attach -t %SCHEDULER_SESSION%
echo To detach from session: Ctrl+B, then D
echo.
echo Application is accessible at: http://localhost:8050
echo Keep this command prompt open to maintain the tmux sessions