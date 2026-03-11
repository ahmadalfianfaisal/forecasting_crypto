#!/bin/bash
# Script otomatisasi penuh untuk setup dan menjalankan aplikasi forecasting dengan tmux persisten

echo "==========================================="
echo "Setup Otomatis Aplikasi Forecasting dengan Tmux"
echo "==========================================="

# Fungsi untuk cek dan install dependensi
setup_dependencies() {
    echo "Memeriksa dan menginstal dependensi..."
    
    # Update package list
    sudo apt update
    
    # Install Python dan pip jika belum ada
    if ! command -v python3 &> /dev/null; then
        echo "Menginstal Python3..."
        sudo apt install -y python3 python3-pip
    fi
    
    # Install tmux jika belum ada
    if ! command -v tmux &> /dev/null; then
        echo "Menginstal Tmux..."
        sudo apt install -y tmux
    fi
    
    # Install git jika belum ada
    if ! command -v git &> /dev/null; then
        echo "Menginstal Git..."
        sudo apt install -y git
    fi
    
    # Install virtualenv jika belum ada
    if ! python3 -m venv --help > /dev/null 2>&1; then
        echo "Menginstal python3-venv..."
        sudo apt install -y python3-venv
    fi
    
    echo "Semua dependensi siap."
}

# Fungsi untuk setup virtual environment dan install requirements
setup_virtual_env() {
    echo "Mempersiapkan virtual environment..."
    
    if [ ! -d "venv" ]; then
        echo "Membuat virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Mengaktifkan virtual environment..."
    source venv/bin/activate
    
    echo "Menginstal requirements..."
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo "File requirements.txt tidak ditemukan!"
        exit 1
    fi
    
    echo "Virtual environment siap."
}

# Fungsi untuk setup tmux dengan konfigurasi optimal
setup_tmux_config() {
    echo "Mengkonfigurasi tmux..."
    
    # Copy tmux config ke home directory
    if [ -f "tmux.conf" ]; then
        cp tmux.conf ~/.tmux.conf
        echo "Konfigurasi tmux telah disalin ke ~/.tmux.conf"
    else
        echo "# Konfigurasi Tmux untuk Aplikasi Forecasting
set -g mouse on
unbind C-b
set-option -g prefix C-a
bind-key C-a send-prefix
set-option -g status-position bottom
set-option -g status-bg black
set-option -g status-fg white
set-option -g status-left-length 40
set-option -g status-right-length 80
set-option -g status-right '#[fg=cyan]%H:%M #[fg=green]%d/%m #[fg=yellow]%Y'
set-window-option -g window-status-current-bg red
set-window-option -g window-status-current-attr bright
set-window-option -g monitor-activity on
set-option -g visual-activity on
set-option -g display-time 3000
set-window-option -g automatic-rename on
set-option -g set-titles on
set-option -g set-titles-string 'Forecast-Vibecoding: #{pane_current_command}'
set-window-option -g mode-keys vi
bind-key -T copy-mode-vi v send-keys -X begin-selection
bind-key -T copy-mode-vi y send-keys -X copy-selection-and-cancel
set-window-option -g remain-on-exit on
bind-key ^s setw synchronize-panes on" > ~/.tmux.conf
    fi
    
    echo "Konfigurasi tmux selesai."
}

# Fungsi untuk menjalankan semua layanan
start_all_services() {
    echo "Menyiapkan dan menjalankan semua layanan..."
    
    # Source virtual environment
    source venv/bin/activate
    
    # Nama session tmux
    APP_SESSION="forecast-app"
    SCHEDULER_SESSION="model-scheduler"
    RETRAIN_SESSION="model-retrain-auto"
    
    # Hentikan sesi yang mungkin masih berjalan
    tmux kill-session -t $APP_SESSION 2>/dev/null || echo "Session $APP_SESSION tidak ditemukan"
    tmux kill-session -t $SCHEDULER_SESSION 2>/dev/null || echo "Session $SCHEDULER_SESSION tidak ditemukan"
    tmux kill-session -t $RETRAIN_SESSION 2>/dev/null || echo "Session $RETRAIN_SESSION tidak ditemukan"
    
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
    
    echo "Semua layanan telah dijalankan dalam sesi tmux."
}

# Fungsi untuk membuat systemd service (opsional)
create_systemd_service() {
    echo "Membuat systemd service untuk menjaga layanan tetap hidup setelah restart..."
    
    # Membuat service untuk aplikasi utama
    sudo tee /etc/systemd/system/forecast-app.service > /dev/null <<EOF
[Unit]
Description=Forecast Vibecoding Application
After=network.target

[Service]
Type=forking
User=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=/usr/bin/tmux new-session -d -s forecast-app 'source $(pwd)/venv/bin/activate && python run_app.py'
ExecStop=/usr/bin/tmux kill-session -t forecast-app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Membuat service untuk scheduler
    sudo tee /etc/systemd/system/model-scheduler.service > /dev/null <<EOF
[Unit]
Description=Model Scheduler Service
After=network.target

[Service]
Type=forking
User=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=/usr/bin/tmux new-session -d -s model-scheduler 'source $(pwd)/venv/bin/activate && python run_scheduler.py'
ExecStop=/usr/bin/tmux kill-session -t model-scheduler
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Membuat service untuk retraining otomatis
    sudo tee /etc/systemd/system/model-retrain-auto.service > /dev/null <<EOF
[Unit]
Description=Automatic Model Retrain Service
After=network.target

[Service]
Type=forking
User=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=/usr/bin/tmux new-session -d -s model-retrain-auto 'source $(pwd)/venv/bin/activate && python -c "from src.services.scheduler_daemon import main; main()"'
ExecStop=/usr/bin/tmux kill-session -t model-retrain-auto
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd dan aktifkan service
    sudo systemctl daemon-reload
    sudo systemctl enable forecast-app.service
    sudo systemctl enable model-scheduler.service
    sudo systemctl enable model-retrain-auto.service
    
    echo "Systemd service telah dibuat dan diaktifkan."
}

# Fungsi utama
main() {
    echo "Mulai proses otomatisasi..."
    
    # Setup dependensi
    setup_dependencies
    
    # Setup virtual environment
    setup_virtual_env
    
    # Setup konfigurasi tmux
    setup_tmux_config
    
    # Jalankan semua layanan
    start_all_services
    
    # Tanyakan apakah ingin membuat systemd service
    read -p "Apakah Anda ingin membuat systemd service agar layanan tetap berjalan setelah restart? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_systemd_service
    fi
    
    echo ""
    echo "==========================================="
    echo "Setup selesai!"
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
    echo ""
    echo "Jika Anda membuat systemd service, layanan akan otomatis berjalan setelah restart server."
    echo "==========================================="
}

# Jalankan fungsi utama
main