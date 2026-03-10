# Langkah-Langkah Final untuk Deployment

## Sebelum Anda Deploy

### 1. Verifikasi RAM User Permissions
- [ ] RAM user dapat login ke Alibaba Cloud Console
- [ ] RAM user memiliki izin akses ke ECS
- [ ] RAM user dapat membuat instance ECS
- [ ] RAM user dapat mengelola security groups
- [ ] Custom policy `ECS-Deployment-Policy` telah dibuat dan diattach ke user

### 2. Siapkan Kode
- [ ] Kode telah diorganisir ke struktur folder yang rapi
- [ ] Semua import statements telah diperbarui
- [ ] File requirements.txt lengkap dan akurat
- [ ] Aplikasi berjalan dengan baik di lokal
- [ ] Semua fungsi utama (forecasting, penanganan negatif, dll.) berfungsi

## Deployment Process

### 3. Buat Instance ECS
- [ ] Login ke Alibaba Cloud Console sebagai RAM user
- [ ] Pilih region yang sesuai
- [ ] Pilih instance type: **ecs.s6-c1m1.large** (1 vCPU, 1 GiB) - atau ecs.t5-lc2m1.nano untuk testing
- [ ] Pilih image: Ubuntu 20.04 LTS 64-bit
- [ ] Konfigurasi storage: 40 GiB Standard SSD
- [ ] Konfigurasi jaringan dan security group
- [ ] Pilih authentication method (password/key pair)
- [ ] Buat instance dan tunggu provisioning selesai

### 4. Konfigurasi Security Group
- [ ] Buka port 22 (SSH)
- [ ] Buka port 80 (HTTP)
- [ ] Buka port 443 (HTTPS)
- [ ] Buka port 8050 (aplikasi Dash)
- [ ] Verifikasi rules telah aktif

### 5. Akses dan Setup Instance
- [ ] SSH ke instance menggunakan IP public
- [ ] Update sistem: `sudo apt update && sudo apt upgrade -y`
- [ ] Install Git: `sudo apt install git -y`
- [ ] Install Python: `sudo apt install python3 python3-pip python3-venv -y`
- [ ] Install Tmux: `sudo apt install tmux -y`

### 6. Deploy Kode
- [ ] Clone repository: `git clone <repo-url> forecast-vibecoding`
- [ ] Pindah ke direktori: `cd forecast-vibecoding`
- [ ] Buat virtual environment: `python3 -m venv venv`
- [ ] Aktifkan virtual environment: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`

### 7. Jalankan Aplikasi dengan Tmux
- [ ] Buat script executable: `chmod +x start_tmux_sessions.sh manage_tmux.sh`
- [ ] Jalankan aplikasi dan scheduler: `./start_tmux_sessions.sh`
- [ ] Verifikasi session berjalan: `./manage_tmux.sh status`
- [ ] Akses aplikasi dari browser: `http://<public-ip>:8050`

## Post-Deployment Verification

### 8. Testing dan Verification
- [ ] Akses aplikasi dari berbagai device/network
- [ ] Test semua fitur forecasting
- [ ] Verifikasi scheduled training berjalan (attach ke scheduler session)
- [ ] Test penanganan nilai negatif
- [ ] Monitor resource usage

### 9. Monitoring Setup
- [ ] Setup logging untuk aplikasi
- [ ] Setup monitoring untuk session
- [ ] Document IP address dan akses

## Troubleshooting

### Jika Aplikasi Tidak Bisa Diakses
1. Cek security group rules
2. Pastikan aplikasi bind ke 0.0.0.0 bukan 127.0.0.1
3. Cek firewall di instance: `sudo ufw status`
4. Cek status session: `./manage_tmux.sh status`
5. Attach ke session: `./manage_tmux.sh attach-app`

### Jika RAM User Tidak Bisa Akses
1. Hubungi administrator RAM untuk memberikan izin ECS
2. Pastikan role yang diberikan cukup untuk operasi yang dibutuhkan

### Jika Memory Penuh
1. Monitor penggunaan: `htop`
2. Restart session jika perlu: `./manage_tmux.sh restart`

## Production Considerations

### Untuk Production Jangka Panjang
- [ ] Pertimbangkan untuk menggunakan systemd service
- [ ] Setup monitoring dan alerting
- [ ] Backup data secara berkala
- [ ] Setup SSL certificate untuk HTTPS
- [ ] Gunakan load balancer jika traffic tinggi

### Untuk Development dan Testing (Saat Ini)
- [ ] Gunakan pendekatan tmux seperti yang telah di-setup
- [ ] Monitor secara manual
- [ ] Backup manual jika diperlukan

## Backup dan Recovery

### Backup Manual
- [ ] Backup data penting: `tar -czf backup-$(date +%Y%m%d).tar.gz mlruns/ models/`
- [ ] Document recovery procedure
- [ ] Test backup dan recovery process

## Ringkasan

Anda sekarang memiliki:
1. Aplikasi forecasting cryptocurrency yang berjalan di Alibaba Cloud ECS
2. Aplikasi utama berjalan di tmux session `forecast-app`
3. Scheduler model berjalan di tmux session `model-scheduler`
4. Akses ke aplikasi web di `http://<public-ip>:8050`
5. Skrip untuk mengelola session tmux

Aplikasi akan tetap berjalan meskipun koneksi SSH Anda terputus berkat penggunaan tmux!

---

Catatan: Untuk production jangka panjang, pertimbangkan untuk mengganti pendekatan tmux dengan systemd service.