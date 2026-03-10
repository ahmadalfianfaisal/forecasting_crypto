# Panduan Deploy Aplikasi ke Alibaba Cloud ECS (Konfigurasi Paling Rendah)

## 1. Persiapan Awal

### 1.1. Mendaftar Akun Alibaba Cloud
1. Kunjungi https://www.alibabacloud.com/
2. Klik "Free Trial" atau "Sign Up"
3. Lengkapi formulir registrasi dan verifikasi akun Anda

### 1.2. Verifikasi Identitas
- Alibaba Cloud membutuhkan verifikasi identitas untuk menggunakan layanan berbayar
- Siapkan dokumen identitas (KTP, SIM, Passport) untuk verifikasi

## 2. Membuat Instance ECS

### 2.1. Akses Console ECS
1. Login ke Alibaba Cloud Console
2. Cari dan klik "Elastic Compute Service (ECS)"
3. Klik "Instances" di menu sebelah kiri
4. Klik "Create Instance"

### 2.2. Konfigurasi Instance (Paling Rendah)
- **Instance Type**: Shared-Compute-Optimized (gunakan instance paling murah seperti `s6` series)
- **Instance Specification**: 1 vCPU, 1 GiB Memory (ecs.s6-c1m1.large)
- **Image**: Ubuntu 20.04 LTS 64-bit
- **Network Type**: VPC (Virtual Private Cloud) - pilih default
- **Security Group**: Buat security group baru atau gunakan default
- **Authentication**: Pilih password atau key pair (disarankan key pair untuk keamanan)

### 2.3. Konfigurasi Storage
- **System Disk**: 40 GiB (standard SSD cukup untuk aplikasi kecil)
- **Data Disk**: Tidak perlu untuk saat ini

### 2.4. Konfigurasi Jaringan
- **Internet Bandwidth**: 1 Mbps (paling rendah dan cukup untuk aplikasi kecil)

### 2.5. Pembayaran
- Pilih durasi sewa (misalnya 1 bulan untuk percobaan)
- Tinjau dan buat instance

## 3. Konfigurasi Security Group

### 3.1. Buka Port yang Diperlukan
1. Di console ECS, klik "Security Groups"
2. Klik security group yang digunakan instance Anda
3. Klik "Add Rule" untuk menambahkan aturan:

| Port Range | Protocol Type | Authorization Policy | Source CIDR |
|------------|---------------|---------------------|-------------|
| 22         | TCP           | Allow              | 0.0.0.0/0   |
| 80         | TCP           | Allow              | 0.0.0.0/0   |
| 443        | TCP           | Allow              | 0.0.0.0/0   |
| 8050       | TCP           | Allow              | 0.0.0.0/0   |

## 4. Akses ke Instance

### 4.1. Dapatkan IP Public
1. Di halaman Instances, temukan instance Anda
2. Catat IP Address Public (Public IP)

### 4.2. SSH ke Instance
```bash
ssh root@<IP_PUBLIC_ANDA>
# atau jika menggunakan user ubuntu
ssh ubuntu@<IP_PUBLIC_ANDA>
```

## 5. Setup Environment di Server

### 5.1. Update Sistem
```bash
sudo apt update && sudo apt upgrade -y
```

### 5.2. Install Python dan Dependencies
```bash
# Install Python 3 dan pip
sudo apt install python3 python3-pip -y

# Install git
sudo apt install git -y

# Install build-essential (jika diperlukan)
sudo apt install build-essential -y
```

### 5.3. Clone Repository
```bash
# Install git jika belum
sudo apt install git -y

# Clone repository Anda
git clone https://github.com/[username]/[repo-name].git
# atau jika Anda menyimpan di folder lokal
cd ~
git clone https://github.com/[username]/[repo-name].git forecast-vibecoding
cd forecast-vibecoding
```

### 5.4. Setup Virtual Environment
```bash
# Install venv
sudo apt install python3-venv -y

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 5.5. Install Dependencies
```bash
# Install dependencies dari requirements.txt
pip install -r requirements.txt

# Install gunicorn untuk production deployment
pip install gunicorn
```

## 6. Konfigurasi Aplikasi

### 6.1. Modifikasi File app.py untuk Production
Ubah baris terakhir di `app.py` dari:
```python
app.run(host="127.0.0.1", port=8050, debug=True)
```
menjadi:
```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
```

### 6.2. Test Aplikasi Secara Lokal
```bash
# Aktifkan virtual environment
source venv/bin/activate

# Jalankan aplikasi
python app.py
```

## 7. Setup Production Deployment

### 7.1. Buat Gunicorn Configuration
Buat file `gunicorn_config.py`:
```python
bind = "0.0.0.0:8050"
workers = 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### 7.2. Test dengan Gunicorn
```bash
# Aktifkan virtual environment
source venv/bin/activate

# Jalankan dengan gunicorn
gunicorn --config gunicorn_config.py app:server
```

## 8. Setup Service untuk Auto-Start

### 8.1. Buat Systemd Service
```bash
sudo nano /etc/systemd/system/dash-app.service
```

Tambahkan konten berikut:
```ini
[Unit]
Description=Dash Application
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/forecast-vibecoding
Environment=PATH=/home/ubuntu/forecast-vibecoding/venv/bin
ExecStart=/home/ubuntu/forecast-vibecoding/venv/bin/gunicorn --config /home/ubuntu/forecast-vibecoding/gunicorn_config.py app:server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8.2. Aktifkan Service
```bash
# Reload daemon
sudo systemctl daemon-reload

# Mulai service
sudo systemctl start dash-app

# Aktifkan auto-start saat boot
sudo systemctl enable dash-app

# Cek status
sudo systemctl status dash-app
```

## 9. Setup Reverse Proxy (Opsional tapi Disarankan)

### 9.1. Install Nginx
```bash
sudo apt install nginx -y
```

### 9.2. Konfigurasi Nginx
```bash
sudo nano /etc/nginx/sites-available/dash-app
```

Tambahkan konfigurasi berikut:
```nginx
server {
    listen 80;
    server_name <IP_PUBLIC_ANDA>;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9.3. Aktifkan Site
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dash-app /etc/nginx/sites-enabled/

# Test konfigurasi
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

## 10. Setup Cron untuk Scheduled Training

### 10.1. Edit Crontab
```bash
crontab -e
```

### 10.2. Tambahkan Schedule (contoh: jalan setiap jam)
```bash
# Jalankan training model setiap jam
0 * * * * cd /home/ubuntu/forecast-vibecoding && source venv/bin/activate && python scheduler.py >> /var/log/training.log 2>&1
```

## 11. Monitoring dan Logging

### 11.1. Lihat Log Aplikasi
```bash
# Lihat log dari systemd service
sudo journalctl -u dash-app -f

# Lihat log dari crontab
tail -f /var/log/training.log
```

## 12. Akses Aplikasi

Aplikasi Anda sekarang bisa diakses melalui:
- http://<IP_PUBLIC_ANDA>:8050 (tanpa nginx)
- http://<IP_PUBLIC_ANDA> (dengan nginx)

## 13. Optimasi Biaya (Opsional)

### 13.1. Gunakan Free Tier
- Cek apakah Alibaba Cloud menyediakan free tier untuk instance tertentu
- Manfaatkan free trial jika tersedia

### 13.2. Shutdown Saat Tidak Digunakan
- Jika hanya digunakan untuk testing, Anda bisa shutdown instance saat tidak digunakan
- Instance yang shutdown masih dikenakan biaya storage

## 14. Backup dan Recovery

### 14.1. Backup Manual
```bash
# Backup data penting ke local
scp -r ubuntu@<IP_PUBLIC_ANDA>:/home/ubuntu/forecast-vibecoding/mlruns ~/backup/
```

### 14.2. Snapshot Instance
- Gunakan fitur snapshot Alibaba Cloud untuk backup instance

## Troubleshooting

### Aplikasi Tidak Bisa Diakses
1. Pastikan security group sudah dibuka untuk port yang digunakan
2. Pastikan firewall lokal tidak memblokir
3. Cek status service: `sudo systemctl status dash-app`
4. Cek log: `sudo journalctl -u dash-app -f`

### Memory Issues
1. Monitor penggunaan memory: `htop`
2. Jika memory penuh, restart service: `sudo systemctl restart dash-app`

### Dependency Issues
1. Pastikan semua dependencies terinstall: `pip install -r requirements.txt`
2. Cek versi Python yang digunakan: `python --version`

---

Catatan Penting:
- Simpan file credential dan API key dengan aman
- Gunakan environment variables untuk menyimpan konfigurasi sensitif
- Monitor penggunaan resource untuk mengoptimalkan biaya
- Backup data secara berkala