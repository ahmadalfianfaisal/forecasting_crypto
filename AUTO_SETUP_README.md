# Setup Otomatis Aplikasi Forecasting dengan Tmux Persisten

File ini berisi skrip otomatisasi untuk menjalankan aplikasi forecasting cryptocurrency dengan sesi tmux persisten yang menjaga aplikasi tetap berjalan meskipun koneksi SSH terputus, serta menjalankan retraining otomatis model secara berkala.

## Daftar File

1. `full_auto_setup.sh` - Skrip setup otomatisasi penuh termasuk pembuatan systemd service
2. `quick_setup.sh` - Skrip setup cepat untuk menjalankan semua layanan
3. `manage_tmux.sh` - Skrip untuk mengelola sesi tmux (sudah diperbarui)
4. `start_all_services.sh` - Skrip untuk menjalankan semua layanan dalam sesi tmux
5. `auto_retrain.sh` - Skrip untuk menjalankan retraining otomatis
6. `PERSISTENT_TMUX_GUIDE.md` - Panduan lengkap penggunaan tmux persisten
7. `tmux.conf` - File konfigurasi tmux yang optimal

## Cara Menggunakan

### 1. Setup Cepat (Direkomendasikan untuk percobaan)

Jalankan skrip setup cepat:

```bash
chmod +x quick_setup.sh
./quick_setup.sh
```

Skrip ini akan:
- Menginstal tmux jika belum terpasang
- Membuat dan mengaktifkan virtual environment
- Menginstal semua dependensi
- Menjalankan semua layanan dalam sesi tmux terpisah

### 2. Setup Otomatisasi Penuh (Direkomendasikan untuk produksi)

Jalankan skrip setup otomatisasi penuh:

```bash
chmod +x full_auto_setup.sh
./full_auto_setup.sh
```

Skrip ini akan:
- Menginstal semua dependensi yang diperlukan
- Membuat dan mengaktifkan virtual environment
- Menginstal semua dependensi Python
- Mengkonfigurasi tmux dengan pengaturan optimal
- Menjalankan semua layanan dalam sesi tmux
- (Opsional) Membuat systemd service agar layanan tetap berjalan setelah restart server

### 3. Menggunakan Skrip Manajemen Tmux

Anda juga bisa menggunakan skrip manajemen yang telah diperbarui:

```bash
# Jalankan semua layanan
./manage_tmux.sh start-all

# Lihat status semua sesi
./manage_tmux.sh status

# Akses sesi aplikasi
./manage_tmux.sh attach-app

# Akses sesi scheduler
./manage_tmux.sh attach-scheduler

# Akses sesi retraining otomatis
./manage_tmux.sh attach-retrain

# Hentikan semua sesi
./manage_tmux.sh stop
```

## Akses Aplikasi

Setelah setup selesai, Anda dapat mengakses aplikasi di:
- Web Interface: `http://[IP_SERVER_ANDA]:8050`

## Menjaga Sesi Tetap Hidup

- Sesi tmux akan tetap berjalan meskipun koneksi SSH Anda terputus
- Untuk melepaskan diri dari sesi tmux tanpa menghentikannya: tekan `Ctrl+B` lalu `D`
- Untuk kembali ke sesi: `tmux attach -t [NAMA_SESSI]`

## Retraining Otomatis

- Retraining otomatis diatur untuk berjalan setiap hari pukul 02:00
- Anda dapat mengubah jadwal dengan mengedit file `src/services/scheduler_daemon.py`
- Log dari proses retraining dapat dilihat di file `scheduler.log`

## Troubleshooting

### Jika tmux tidak dikenali:
```bash
sudo apt update
sudo apt install tmux
```

### Jika virtual environment tidak aktif:
```bash
source venv/bin/activate
```

### Jika dependensi tidak terinstal:
```bash
pip install -r requirements.txt
```

### Melihat semua sesi tmux:
```bash
tmux ls
```

## Catatan Penting

- Pastikan instance Anda memiliki cukup resource (RAM dan CPU) untuk menjalankan semua layanan
- Monitor penggunaan resource secara berkala
- Jika Anda menggunakan `full_auto_setup.sh` dengan systemd service, layanan akan otomatis berjalan setelah restart server
- Simpan credential dan API key dengan aman