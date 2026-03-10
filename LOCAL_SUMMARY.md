# Ringkasan: Jalankan Aplikasi Secara Lokal dengan Tmux

## Tujuan
Menjalankan aplikasi forecasting cryptocurrency secara lokal di komputer Anda dengan:
- Aplikasi web berjalan di http://localhost:8050
- Scheduled training berjalan terus-menerus
- Aplikasi tetap berjalan meskipun terminal ditutup (dengan tmux)

## File-file yang Dibuat
- `start_local_tmux_sessions.bat` - Script untuk jalankan aplikasi di WSL dengan tmux
- `start_local_jobs.ps1` - Script alternatif untuk PowerShell jobs
- `LOCAL_TMUX_GUIDE.md` - Panduan lengkap penggunaan lokal

## Prasyarat
- Windows 10/11 dengan WSL2
- Python 3.8+
- Virtual environment dengan semua dependencies

## Cara Jalankan

### 1. Setup WSL dan Tmux
```cmd
wsl --install -d Ubuntu
wsl
sudo apt update && sudo apt install tmux -y
```

### 2. Setup Virtual Environment
```bash
cd /mnt/c/Users/admin/alibaba-cloud/forecast-vibecoding
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```cmd
start_local_tmux_sessions.bat
```

### 4. Akses Aplikasi
- Web: http://localhost:8050
- Tmux app: `wsl tmux attach -t forecast-app-local`
- Tmux scheduler: `wsl tmux attach -t model-scheduler-local`

## Kelebihan Pendekatan Ini
- ✅ Aplikasi berjalan secara lokal
- ✅ Scheduled training aktif
- ✅ Tidak perlu deploy ke cloud
- ✅ Bisa diakses di localhost
- ✅ Session tetap aktif meskipun terminal ditutup (dengan tmux)

## Kekurangan
- ❌ Hanya berjalan saat komputer menyala
- ❌ Bergantung pada WSL
- ❌ Tidak bisa diakses dari luar jaringan lokal

## Alternatif Tanpa WSL
Gunakan `start_local_jobs.ps1` untuk PowerShell jobs (tapi job akan berhenti saat PowerShell ditutup).

## Catatan
- Pastikan WSL tetap berjalan agar tmux sessions tetap aktif
- Aplikasi akan berhenti saat komputer dimatikan
- Ideal untuk development dan testing lokal

---

Gunakan pendekatan ini untuk menjalankan aplikasi forecasting Anda secara lokal dengan scheduled training!