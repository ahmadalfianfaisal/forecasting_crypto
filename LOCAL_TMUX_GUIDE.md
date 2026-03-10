# Panduan Jalankan Aplikasi Secara Lokal dengan Tmux

## Deskripsi
Dokumentasi ini menjelaskan cara menjalankan aplikasi forecasting cryptocurrency secara lokal di komputer Anda menggunakan tmux untuk menjaga aplikasi tetap berjalan meskipun Anda menutup terminal.

## Prasyarat
- Windows 10/11 dengan WSL2 (Windows Subsystem for Linux) terinstall
- Python 3.8+ terinstall
- Virtual environment sudah disiapkan
- Tmux terinstall di WSL

## Instalasi WSL dan Tmux

### 1. Instal WSL2
Buka PowerShell sebagai Administrator dan jalankan:
```powershell
wsl --install -d Ubuntu
```

### 2. Instal Tmux di WSL
Setelah WSL terinstall dan Anda masuk ke dalamnya:
```bash
sudo apt update
sudo apt install tmux -y
```

### 3. Setup Virtual Environment
Di direktori proyek Anda:
```bash
python -m venv venv
# Di Windows
venv\Scripts\activate
# Install dependencies
pip install -r requirements.txt
```

## Jalankan Aplikasi Secara Lokal

### 1. Gunakan Script Otomatis
Jalankan script yang telah disediakan:
```cmd
start_local_tmux_sessions.bat
```

Script ini akan:
- Membuat session tmux untuk aplikasi utama (forecast-app-local)
- Membuat session tmux untuk scheduler (model-scheduler-local)
- Menjalankan aplikasi Dash di port 8050
- Menjalankan scheduler untuk pelatihan model otomatis

### 2. Akses Aplikasi
Setelah dijalankan, Anda bisa mengakses:
- Aplikasi web: http://localhost:8050
- Akses session aplikasi: `wsl tmux attach -t forecast-app-local`
- Akses session scheduler: `wsl tmux attach -t model-scheduler-local`

## Alternatif: Gunakan PowerShell Jobs

Jika Anda tidak ingin menggunakan WSL, Anda bisa menggunakan PowerShell jobs:

### 1. Jalankan dengan PowerShell
```powershell
.\start_local_jobs.ps1
```

### 2. Akses Aplikasi
- Aplikasi web: http://localhost:8050
- Cek status job: `Get-Job`
- Lihat output job: `Receive-Job -Name "ForecastApp"`

## Mengelola Session

### Di WSL dengan Tmux:
```bash
# Lihat semua session
wsl tmux ls

# Attach ke session aplikasi
wsl tmux attach -t forecast-app-local

# Attach ke session scheduler
wsl tmux attach -t model-scheduler-local

# Detach dari session (di dalam session tmux): Ctrl+B lalu D

# Hentikan session
wsl tmux kill-session -t forecast-app-local
wsl tmux kill-session -t model-scheduler-local
```

### Di PowerShell:
```powershell
# Lihat semua job
Get-Job

# Hentikan job
Stop-Job -Name "ForecastApp"
Stop-Job -Name "ModelScheduler"

# Hapus job
Remove-Job -Name "ForecastApp"
Remove-Job -Name "ModelScheduler"
```

## Keep Sessions Running

### Untuk WSL + Tmux:
- **Keuntungan**: Session akan tetap berjalan bahkan setelah menutup terminal
- **Catatan**: Pastikan WSL tetap berjalan (tidak shutdown)

### Untuk PowerShell Jobs:
- **Kekurangan**: Job akan berhenti saat PowerShell session ditutup
- **Solusi**: Gunakan Windows Task Scheduler untuk menjaga aplikasi tetap berjalan

## Windows Task Scheduler Setup (Opsional)

Untuk menjaga aplikasi tetap berjalan setelah restart komputer:

1. Buka Task Scheduler
2. Buat Basic Task baru
3. Set trigger: "When the computer starts"
4. Set action: "Start a program"
5. Program: `C:\path\to\your\python.exe`
6. Arguments: `run_app.py`
7. Start in: `C:\path\to\your\project`

## Monitoring dan Troubleshooting

### Cek Apakah Aplikasi Berjalan
- Buka browser dan akses http://localhost:8050
- Cek session tmux: `wsl tmux ls`
- Cek job PowerShell: `Get-Job`

### Troubleshooting Umum
1. **Aplikasi tidak bisa diakses di localhost:8050**
   - Pastikan port 8050 tidak digunakan aplikasi lain
   - Cek apakah session tmux benar-benar berjalan

2. **Tmux tidak bisa membuat session**
   - Pastikan WSL berjalan
   - Pastikan tmux terinstall: `wsl which tmux`

3. **Virtual environment tidak aktif**
   - Pastikan venv dibuat dan aktif
   - Cek apakah semua dependencies terinstall

## Scheduled Training
- Scheduler akan berjalan terus-menerus di background
- Melakukan pelatihan model secara berkala
- Bisa dimonitor lewat session scheduler

## Catatan Penting
- Aplikasi akan berjalan selama komputer Anda menyala dan WSL aktif
- Untuk production jangka panjang, pertimbangkan untuk deploy ke cloud
- Simpan credential dan API key dengan aman

---

Dengan pendekatan ini, Anda bisa menjalankan aplikasi forecasting cryptocurrency Anda secara lokal dengan scheduled training yang tetap berjalan!