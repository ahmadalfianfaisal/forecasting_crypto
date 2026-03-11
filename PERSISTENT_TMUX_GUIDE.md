# Panduan Penggunaan Tmux Persisten dengan Retraining Otomatis

## Deskripsi
Dokumentasi ini menjelaskan cara menjalankan aplikasi forecasting cryptocurrency dengan sesi tmux persisten yang menjaga aplikasi tetap berjalan meskipun koneksi SSH terputus, serta menjalankan retraining otomatis model secara berkala.

## Instalasi Tmux di Server Ubuntu

Jika tmux belum terinstall di server Anda, instal terlebih dahulu:
```bash
sudo apt update
sudo apt install -y tmux
```

## Setup Virtual Environment

Pastikan virtual environment sudah disiapkan:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Layanan dengan Tmux Persisten

### 1. Jalankan Semua Layanan (Aplikasi Utama + Scheduler + Retraining Otomatis)
```bash
./manage_tmux.sh start-all
```

### 2. Jalankan Hanya Retraining Otomatis
```bash
./manage_tmux.sh start-retrain
```

### 3. Jalankan Hanya Aplikasi dan Scheduler (tanpa retraining otomatis)
```bash
./manage_tmux.sh start
```

## Mengelola Sesi Tmux

### Lihat Semua Sesi
```bash
./manage_tmux.sh status
# Atau langsung dengan perintah tmux
tmux ls
```

### Akses Sesi
- Aplikasi utama: `./manage_tmux.sh attach-app` atau `tmux attach -t forecast-app`
- Scheduler: `./manage_tmux.sh attach-scheduler` atau `tmux attach -t model-scheduler`
- Retraining otomatis: `./manage_tmux.sh attach-retrain` atau `tmux attach -t model-retrain-auto`

### Lepaskan Diri dari Sesi
Saat berada di dalam sesi tmux, tekan `Ctrl+B` lalu tekan `D` untuk melepaskan diri dari sesi tanpa menghentikannya.

### Hentikan Semua Sesi
```bash
./manage_tmux.sh stop
```

### Restart Semua Sesi
```bash
./manage_tmux.sh restart-all
```

## Retraining Otomatis

### Skema Retraining
Retraining otomatis diatur dalam file `src/services/scheduler_daemon.py`:
- Secara default dijadwalkan untuk berjalan setiap hari pukul 02:00
- Anda dapat mengubah jadwal dengan mengedit file tersebut

### Logging
- Log dari proses retraining dapat ditemukan di file `scheduler.log`
- Anda juga dapat melihat log secara langsung dengan mengakses sesi retraining

## Menjaga Sesi Tetap Hidup

### Di Server Ubuntu:
- Sesi tmux akan terus berjalan meskipun koneksi SSH terputus
- Server harus tetap menyala agar sesi tetap berjalan
- Untuk memastikan server tetap menyala, hindari restart atau shutdown

### Untuk Keamanan Jangka Panjang:
- Pertimbangkan untuk menggunakan systemd service untuk menjaga layanan tetap berjalan setelah restart server
- Monitor penggunaan resource (CPU dan RAM) untuk mencegah overload

## Contoh Pembuatan Service Systemd (Opsional)

Jika Anda ingin layanan tetap berjalan setelah restart server, Anda bisa membuat systemd service:

1. Buat file service:
```bash
sudo nano /etc/systemd/system/forecast-app.service
```

2. Tambahkan konten berikut (sesuaikan path direktori Anda):
```ini
[Unit]
Description=Forecast Vibecoding Application
After=network.target

[Service]
Type=forking
User=your_username
WorkingDirectory=/path/to/forecast-vibecoding
ExecStart=/usr/bin/tmux new-session -d -s forecast-app 'source venv/bin/activate && python run_app.py'
ExecStop=/usr/bin/tmux kill-session -t forecast-app
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Ulangi langkah di atas untuk scheduler dan retraining otomatis

4. Aktifkan service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable forecast-app.service
sudo systemctl start forecast-app.service
```

## Troubleshooting

### Sesi Tmux Tidak Muncul
- Pastikan tmux terinstall: `which tmux`
- Periksa apakah virtual environment aktif
- Pastikan semua dependencies terinstall

### Aplikasi Tidak Bisa Diakses
- Pastikan port 8050 tidak digunakan oleh aplikasi lain
- Cek firewall dan security group server Anda
- Pastikan sesi tmux benar-benar berjalan

### Retraining Tidak Berjalan
- Cek log di file `scheduler.log`
- Pastikan sesi retraining otomatis berjalan: `tmux ls`
- Pastikan waktu server sesuai dengan jadwal retraining

## Catatan Penting
- Pastikan server Anda memiliki cukup resource (RAM dan CPU) untuk menjalankan semua layanan
- Monitor penggunaan resource secara berkala
- Backup data dan model secara rutin
- Simpan credential dan API key dengan aman