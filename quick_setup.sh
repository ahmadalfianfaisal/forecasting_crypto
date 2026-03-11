#!/bin/bash
# Script setup cepat untuk menjalankan aplikasi forecasting dengan tmux persisten

echo "==========================================="
echo "Setup Cepat Aplikasi Forecasting dengan Tmux"
echo "==========================================="

# Cek dan install tmux jika belum ada
if ! command -v tmux &> /dev/null; then
    echo "Menginstal Tmux..."
    sudo apt update
    sudo apt install -y tmux
fi

# Setup virtual environment
if [ ! -d "venv" ]; then
    echo "Membuat virtual environment..."
    python3 -m venv venv
fi

echo "Mengaktifkan virtual environment..."
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "Menginstal requirements..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "File requirements.txt tidak ditemukan!"
    exit 1
fi

# Mulai semua layanan dalam sesi tmux
echo "Menjalankan semua layanan dalam sesi tmux..."

# Nama session tmux
APP_SESSION="forecast-app"
SCHEDULER_SESSION="model-scheduler"
RETRAIN_SESSION="model-retrain-auto"

# Hentikan sesi yang mungkin masih berjalan
tmux kill-session -t $APP_SESSION 2>/dev/null || true
tmux kill-session -t $SCHEDULER_SESSION 2>/dev/null || true
tmux kill-session -t $RETRAIN_SESSION 2>/dev/null || true

sleep 2

# Buat session tmux untuk aplikasi utama
echo "Membuat session tmux untuk aplikasi utama: $APP_SESSION"
tmux new-session -d -s $APP_SESSION
tmux send-keys -t $APP_SESSION "source venv/bin/activate" Enter
tmux send-keys -t $APP_SESSION "python run_app.py" Enter

# Buat session tmux untuk scheduler
echo "Membuat session tmux untuk scheduler: $SCHEDULER_SESSION"
tmux new-session -d -s $SCHEDULER_SESSION
tmux send-keys -t $SCHEDULER_SESSION "source venv/bin/activate" Enter
tmux send-keys -t $SCHEDULER_SESSION "python run_scheduler.py" Enter

# Buat session tmux untuk retraining otomatis
echo "Membuat session tmux untuk retraining otomatis: $RETRAIN_SESSION"
tmux new-session -d -s $RETRAIN_SESSION
tmux send-keys -t $RETRAIN_SESSION "source venv/bin/activate" Enter
tmux send-keys -t $RETRAIN_SESSION "python -c \"from src.services.scheduler_daemon import main; main()\"" Enter

echo ""
echo "==========================================="
echo "Setup cepat selesai!"
echo "==========================================="
echo ""
echo "Layanan yang sedang berjalan:"
echo "- Aplikasi utama: forecast-app"
echo "- Scheduler: model-scheduler"
echo "- Retraining otomatis: model-retrain-auto"
echo ""
echo "Status sesi tmux:"
tmux ls
echo ""
echo "Aplikasi dapat diakses di: http://$(curl -s ifconfig.me):8050"
echo ""
echo "Perintah utilitas:"
echo "- Lihat semua sesi: tmux ls"
echo "- Akses aplikasi: tmux attach -t forecast-app"
echo "- Akses scheduler: tmux attach -t model-scheduler"
echo "- Akses retraining: tmux attach -t model-retrain-auto"
echo "- Lepaskan sesi: Ctrl+B lalu D"
echo "==========================================="