# Deployment Checklist - Alibaba Cloud ECS

## Pra-Deployment

### 1. Verifikasi RAM User Permissions
- [ ] RAM user dapat login ke Alibaba Cloud Console
- [ ] RAM user memiliki izin akses ke ECS
- [ ] RAM user dapat membuat instance ECS
- [ ] RAM user dapat mengelola security groups
- [ ] RAM user dapat mengelola VPC (jika diperlukan)

### 2. Verifikasi Kode dan Dependencies
- [ ] Kode telah diorganisir ke struktur folder yang rapi
- [ ] Semua import statements telah diperbarui
- [ ] File requirements.txt lengkap dan akurat
- [ ] Aplikasi berjalan dengan baik di lokal
- [ ] Semua fungsi utama (forecasting, penanganan negatif, dll.) berfungsi

### 3. Backup dan Persiapan
- [ ] Backup kode ke repository (GitHub, GitLab, dll.)
- [ ] Backup data penting (model, database, dll.)
- [ ] Siapkan dokumentasi deployment
- [ ] Siapkan credential dan API keys (jika ada)

## Deployment Process

### 4. Membuat Instance ECS
- [ ] Login ke Alibaba Cloud Console sebagai RAM user
- [ ] Pilih region yang sesuai
- [ ] Pilih instance type: ecs.s6-c1m1.large (1 vCPU, 1 GiB)
- [ ] Pilih image: Ubuntu 20.04 LTS 64-bit
- [ ] Konfigurasi storage: 40 GiB Standard SSD
- [ ] Konfigurasi jaringan dan security group
- [ ] Pilih authentication method (password/key pair)
- [ ] Buat instance dan tunggu provisioning selesai

### 5. Konfigurasi Security Group
- [ ] Buka port 22 (SSH)
- [ ] Buka port 80 (HTTP)
- [ ] Buka port 443 (HTTPS)
- [ ] Buka port 8050 (aplikasi Dash)
- [ ] Verifikasi rules telah aktif

### 6. Akses dan Setup Instance
- [ ] SSH ke instance menggunakan IP public
- [ ] Update sistem: `sudo apt update && sudo apt upgrade -y`
- [ ] Install Git: `sudo apt install git -y`
- [ ] Install Python: `sudo apt install python3 python3-pip python3-venv -y`

### 7. Deploy Kode
- [ ] Clone repository: `git clone <repo-url> forecast-vibecoding`
- [ ] Pindah ke direktori: `cd forecast-vibecoding`
- [ ] Buat virtual environment: `python3 -m venv venv`
- [ ] Aktifkan virtual environment: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`

### 8. Uji Aplikasi
- [ ] Jalankan aplikasi: `python src/views/app.py`
- [ ] Akses dari browser: `http://<public-ip>:8050`
- [ ] Verifikasi semua fungsi berjalan
- [ ] Pastikan tidak ada error

## Production Setup

### 9. Setup Gunicorn dan Service
- [ ] Install Gunicorn: `pip install gunicorn`
- [ ] Test Gunicorn: `gunicorn --bind 0.0.0.0:8050 src.views.app:app.server`
- [ ] Buat systemd service file
- [ ] Aktifkan dan start service
- [ ] Verifikasi service berjalan: `sudo systemctl status dash-app`

### 10. Setup Scheduled Training
- [ ] Buat systemd service untuk scheduler
- [ ] Aktifkan dan start scheduler service
- [ ] Verifikasi scheduler berjalan: `sudo systemctl status model-scheduler`

### 11. Setup Reverse Proxy (Opsional)
- [ ] Install Nginx: `sudo apt install nginx -y`
- [ ] Konfigurasi Nginx sebagai reverse proxy
- [ ] Test akses melalui port 80

## Post-Deployment

### 12. Testing dan Verification
- [ ] Akses aplikasi dari berbagai device/network
- [ ] Test semua fitur forecasting
- [ ] Verifikasi scheduled training berjalan
- [ ] Test penanganan nilai negatif
- [ ] Monitor resource usage

### 13. Monitoring Setup
- [ ] Setup logging untuk aplikasi
- [ ] Setup monitoring untuk service
- [ ] Setup alert jika service down
- [ ] Document IP address dan akses

### 14. Backup Strategy
- [ ] Setup backup otomatis untuk data penting
- [ ] Document recovery procedure
- [ ] Test backup dan recovery process

## Security dan Maintenance

### 15. Security Hardening
- [ ] Update dan patch sistem secara berkala
- [ ] Setup firewall rules
- [ ] Monitor access logs
- [ ] Rotate credentials secara berkala

### 16. Maintenance Schedule
- [ ] Jadwal maintenance untuk update sistem
- [ ] Jadwal backup data
- [ ] Monitoring kesehatan aplikasi
- [ ] Monitoring penggunaan resource

## Rollback Plan

### 17. Prosedur Rollback
- [ ] Document cara rollback ke versi sebelumnya
- [ ] Backup konfigurasi sebelumnya
- [ ] Test rollback procedure
- [ ] Siapkan contact person untuk bantuan

---

Catatan Penting:
- Simpan checklist ini sebagai referensi
- Tandai setiap item saat selesai
- Document setiap langkah untuk referensi masa depan
- Backup semua konfigurasi penting