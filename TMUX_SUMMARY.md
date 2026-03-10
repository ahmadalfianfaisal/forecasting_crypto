# Ringkasan Deployment dengan Tmux

## Pendekatan yang Digunakan
Kami telah mengatur sistem deployment aplikasi forecasting cryptocurrency menggunakan **tmux** untuk menjaga aplikasi tetap berjalan meskipun koneksi SSH terputus.

## File-file yang Dibuat

### 1. Script Otomasi
- `start_tmux_sessions.sh` - Script untuk memulai session tmux untuk aplikasi dan scheduler
- `manage_tmux.sh` - Script untuk mengelola session (start, stop, restart, attach, dll.)
- `setup_server.sh` - Script untuk setup awal di server

### 2. Entry Point Aplikasi
- `run_app.py` - Entry point untuk aplikasi utama
- `run_scheduler.py` - Entry point untuk scheduler model

### 3. Dokumentasi
- `TMUX_DEPLOYMENT_GUIDE.md` - Panduan lengkap penggunaan tmux untuk deployment

## Cara Deploy

### 1. Di Server
```bash
# Clone atau upload repository
git clone <repository-url>
cd forecast-vibecoding

# Setup awal
chmod +x setup_server.sh
./setup_server.sh

# Jalankan aplikasi dan scheduler
chmod +x start_tmux_sessions.sh
chmod +x manage_tmux.sh
./start_tmux_sessions.sh
```

### 2. Setelah Deploy
```bash
# Lihat status session
./manage_tmux.sh status

# Attach ke aplikasi
./manage_tmux.sh attach-app

# Attach ke scheduler
./manage_tmux.sh attach-scheduler

# Restart jika perlu
./manage_tmux.sh restart
```

## Kelebihan Pendekatan Tmux
- **Simpel dan cepat** untuk setup
- **Session tetap aktif** meskipun koneksi SSH terputus
- **Mudah untuk debugging** dan monitoring
- **Tidak perlu setup systemd service**

## Akses Aplikasi
- Aplikasi web: `http://<IP_SERVER_ANDA>:8050`
- Akses tmux: `./manage_tmux.sh attach-app`
- Scheduler: `./manage_tmux.sh attach-scheduler`

## Monitoring
- Aplikasi tetap berjalan di background
- Bisa attach ke session untuk melihat log secara real-time
- Mudah untuk troubleshooting

## Catatan Penting
- Tmux adalah solusi yang baik untuk development dan testing
- Untuk production jangka panjang, pertimbangkan systemd service
- Aplikasi tidak otomatis restart saat server reboot (kecuali ditambahkan ke crontab)

## Troubleshooting
- Jika aplikasi tidak bisa diakses, cek security group
- Jika session tidak muncul, cek apakah tmux terinstall
- Jika virtual environment tidak aktif, cek path dan dependencies

---

Proyek Anda sekarang siap untuk deployment menggunakan tmux. Ikuti panduan di `TMUX_DEPLOYMENT_GUIDE.md` untuk instruksi lengkap.