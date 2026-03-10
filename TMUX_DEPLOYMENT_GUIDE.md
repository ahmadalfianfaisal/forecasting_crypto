# Panduan Deployment dengan Tmux

## Deskripsi
Dokumentasi ini menjelaskan cara menjalankan aplikasi forecasting cryptocurrency menggunakan tmux untuk menjaga aplikasi tetap berjalan meskipun koneksi SSH terputus.

## Prasyarat
- Server Linux (Ubuntu 20.04 LTS direkomendasikan)
- Akses SSH ke server
- tmux terinstall
- Python dan virtual environment sudah disiapkan

## Instalasi Tmux
Jika tmux belum terinstall:
```bash
sudo apt update
sudo apt install tmux -y
```

## Setup dan Jalankan Aplikasi

### 1. Clone Repository
```bash
git clone <repository-url> forecast-vibecoding
cd forecast-vibecoding
```

### 2. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi dengan Tmux
Gunakan script yang telah disediakan:
```bash
chmod +x start_tmux_sessions.sh
chmod +x manage_tmux.sh
./start_tmux_sessions.sh
```

Script ini akan:
- Membuat session tmux untuk aplikasi utama (forecast-app)
- Membuat session tmux untuk scheduler (model-scheduler)
- Menjalankan aplikasi Dash di port 8050
- Menjalankan scheduler untuk pelatihan model otomatis

## Mengelola Session Tmux

Gunakan script manage_tmux.sh untuk mengelola session:

```bash
# Mulai semua session
./manage_tmux.sh start

# Hentikan semua session
./manage_tmux.sh stop

# Restart semua session
./manage_tmux.sh restart

# Lihat status semua session
./manage_tmux.sh status

# Attach ke session aplikasi
./manage_tmux.sh attach-app

# Attach ke session scheduler
./manage_tmux.sh attach-scheduler
```

## Akses Aplikasi

Setelah aplikasi berjalan, Anda bisa mengakses:
- Aplikasi web: http://<IP_SERVER_ANDA>:8050
- Akses melalui tmux: Gunakan `./manage_tmux.sh attach-app`

## Monitoring dan Troubleshooting

### Melihat Output Aplikasi
```bash
# Attach ke session aplikasi
./manage_tmux.sh attach-app

# Tekan Ctrl+B lalu D untuk detach
```

### Melihat Output Scheduler
```bash
# Attach ke session scheduler
./manage_tmux.sh attach-scheduler

# Tekan Ctrl+B lalu D untuk detach
```

### Cek Status Semua Session
```bash
./manage_tmux.sh status
```

## Menjaga Aplikasi Tetap Berjalan

### Otomatisasi saat Boot (opsional)
Jika ingin aplikasi otomatis berjalan saat server restart, Anda bisa menambahkan ke crontab:

```bash
# Edit crontab
crontab -e

# Tambahkan baris berikut untuk menjalankan saat boot
@reboot cd /home/ubuntu/forecast-vibecoding && chmod +x manage_tmux.sh && ./manage_tmux.sh start
```

## Perintah Tmux Dasar

Jika Anda perlu menggunakan tmux secara langsung:

### Membuat Session Baru
```bash
tmux new-session -d -s session_name
```

### Mengirim Perintah ke Session
```bash
tmux send-keys -t session_name 'command' Enter
```

### Attach ke Session
```bash
tmux attach -t session_name
```

### Detach dari Session
- Dalam session tmux: Tekan `Ctrl+B` lalu `D`

### Lihat Semua Session
```bash
tmux ls
```

### Hentikan Session
```bash
tmux kill-session -t session_name
```

## Troubleshooting Umum

### 1. Aplikasi tidak bisa diakses dari web
- Pastikan port 8050 terbuka di security group
- Cek apakah aplikasi benar-benar berjalan: `./manage_tmux.sh attach-app`

### 2. Tmux tidak bisa membuat session
- Pastikan tmux terinstall: `which tmux`
- Cek permission file: `chmod +x *.sh`

### 3. Virtual environment tidak aktif
- Pastikan venv dibuat dan aktif: `source venv/bin/activate`
- Cek apakah semua dependencies terinstall

### 4. Scheduler tidak berjalan
- Cek log scheduler: `./manage_tmux.sh attach-scheduler`
- Pastikan semua dependencies scheduler terinstall

## Keamanan

- Simpan credential dan API key dengan aman
- Gunakan environment variables untuk konfigurasi sensitif
- Monitor akses ke server secara berkala

## Backup dan Recovery

- Backup data penting secara berkala
- Simpan konfigurasi tmux dan script management
- Document prosedur recovery

---

Catatan: Tmux adalah solusi yang baik untuk development dan testing. Untuk production jangka panjang, pertimbangkan untuk menggunakan systemd service.