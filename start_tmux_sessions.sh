#!/bin/bash
# Script untuk setup dan menjalankan aplikasi forecasting dengan tmux

# Nama session tmux
APP_SESSION="forecast-app"
SCHEDULER_SESSION="model-scheduler"

echo "Setting up tmux sessions for forecast application..."

# Cek apakah tmux sudah terinstall
if ! command -v tmux &> /dev/null; then
    echo "Installing tmux..."
    sudo apt update
    sudo apt install -y tmux
fi

# Setup virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Buat session tmux untuk aplikasi utama
echo "Creating tmux session for main application: $APP_SESSION"
tmux new-session -d -s $APP_SESSION

# Kirim perintah ke session aplikasi
tmux send-keys -t $APP_SESSION "source venv/bin/activate" Enter
tmux send-keys -t $APP_SESSION "python run_app.py" Enter

echo "Application started in tmux session: $APP_SESSION"
echo "Access via: tmux attach -t $APP_SESSION"
echo "Or access via web browser: http://<your-server-ip>:8050"

# Buat session tmux untuk scheduler
echo "Creating tmux session for model scheduler: $SCHEDULER_SESSION"
tmux new-session -d -s $SCHEDULER_SESSION

# Kirim perintah ke session scheduler
tmux send-keys -t $SCHEDULER_SESSION "source venv/bin/activate" Enter
tmux send-keys -t $SCHEDULER_SESSION "python run_scheduler.py" Enter

echo "Scheduler started in tmux session: $SCHEDULER_SESSION"
echo "Access via: tmux attach -t $SCHEDULER_SESSION"

echo ""
echo "Both sessions are now running in the background!"
echo ""
echo "To view sessions: tmux ls"
echo "To attach to app: tmux attach -t $APP_SESSION"
echo "To attach to scheduler: tmux attach -t $SCHEDULER_SESSION"
echo "To detach from session: Ctrl+B, then D"
echo ""
echo "Application is accessible at: http://<your-server-ip>:8050"