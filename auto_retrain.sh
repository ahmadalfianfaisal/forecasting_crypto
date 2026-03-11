#!/bin/bash
# Script untuk menjalankan retraining otomatis model

# Nama session tmux untuk retraining otomatis
RETRAIN_SESSION="model-retrain-auto"

echo "Setting up automatic model retraining..."

# Cek apakah tmux sudah terinstall
if ! command -v tmux &> /dev/null; then
    echo "Installing tmux..."
    sudo apt update
    sudo apt install -y tmux
fi

# Setup virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Buat session tmux untuk retraining otomatis
echo "Creating tmux session for automatic retraining: $RETRAIN_SESSION"
tmux new-session -d -s $RETRAIN_SESSION

# Kirim perintah ke session retraining
tmux send-keys -t $RETRAIN_SESSION "source venv/bin/activate" Enter
tmux send-keys -t $RETRAIN_SESSION "python -c \"from src.services.scheduler_daemon import main; main()\"" Enter

echo "Automatic retraining started in tmux session: $RETRAIN_SESSION"
echo "Access via: tmux attach -t $RETRAIN_SESSION"

echo ""
echo "Session is now running in the background!"
echo ""
echo "To view sessions: tmux ls"
echo "To attach to retraining: tmux attach -t $RETRAIN_SESSION"
echo "To detach from session: Ctrl+B, then D"
echo ""