# Panduan Deploy ke Alibaba Cloud ECS Menggunakan RAM User

## Prasyarat
- Anda memiliki RAM user account di Alibaba Cloud
- RAM user memiliki izin untuk mengakses ECS (Elastic Compute Service)
- Anda memiliki akses ke Alibaba Cloud Console

## 1. Verifikasi Hak Akses RAM User

### 1.1. Login ke Alibaba Cloud Console
1. Buka browser dan kunjungi: https://home.console.aliyun.com/
2. Login menggunakan credentials RAM user Anda
3. Pastikan Anda bisa mengakses console

### 1.2. Verifikasi Izin ECS
1. Di Alibaba Cloud Console, cari dan klik "ECS" (Elastic Compute Service)
2. Pastikan Anda bisa melihat halaman ECS
3. Jika muncul pesan "Access Denied", hubungi administrator RAM untuk memberikan izin berikut:
   - AliyunECSFullAccess (untuk akses penuh ke ECS)
   - Atau setidaknya:
     - ecs:DescribeInstances
     - ecs:CreateInstance
     - ecs:DeleteInstance
     - ecs:StartInstance
     - ecs:StopInstance

## 2. Membuat Instance ECS

### 2.1. Akses Halaman ECS
1. Di Alibaba Cloud Console, klik "Products" di kiri atas
2. Cari dan klik "Elastic Compute Service (ECS)"
3. Klik "Instances" di menu sebelah kiri

### 2.2. Buat Instance Baru
1. Klik tombol "Create Instance"
2. Pilih opsi berikut untuk konfigurasi paling rendah:
   - **Billing Method**: Subscription atau Pay-As-You-Go (Pay-As-You-Go lebih fleksibel untuk testing)
   - **Instance Family**: Shared-Compute-Optimized (s6) - paling hemat biaya
   - **Instance Type**: ecs.s6-c1m1.large (1 vCPU, 1 GiB Memory)
   - **Image**: Ubuntu 20.04 LTS 64-bit
   - **Storage**: 40 GiB Standard SSD
   - **Network**: VPC (gunakan default jika tersedia)
   - **Security Group**: Gunakan default atau buat baru

### 2.3. Konfigurasi Keamanan
1. **Authentication Method**: Pilih Password atau Key Pair
   - Jika menggunakan password, buat password kuat
   - Jika menggunakan key pair, simpan file .pem dengan aman

2. **Network Billing Type**: 
   - Bandwidth: 1 Mbps (paling rendah untuk testing)

### 2.4. Tinjau dan Buat
1. Tinjau konfigurasi Anda
2. Centang "I acknowledge that I will be charged for the resources I use"
3. Klik "Create Instance"
4. Bayar jika diminta (jika menggunakan subscription)

## 3. Konfigurasi Security Group

### 3.1. Akses Security Group
1. Di ECS Console, klik "Network & Security" → "Security Groups"
2. Temukan security group yang digunakan instance Anda

### 3.2. Tambahkan Aturan
Tambahkan aturan berikut untuk membuka port yang dibutuhkan:

| Port Range | Protocol Type | Authorization Policy | Source CIDR |
|------------|---------------|---------------------|-------------|
| 22         | TCP           | Allow              | 0.0.0.0/0   |
| 80         | TCP           | Allow              | 0.0.0.0/0   |
| 443        | TCP           | Allow              | 0.0.0.0/0   |
| 8050       | TCP           | Allow              | 0.0.0.0/0   |

## 4. Akses ke Instance

### 4.1. Dapatkan IP Public
1. Kembali ke halaman "Instances"
2. Temukan instance Anda
3. Catat IP Address di kolom "Public IP Address"

### 4.2. SSH ke Instance
```bash
ssh root@<PUBLIC_IP_ADDRESS>
# atau jika menggunakan user ubuntu
ssh ubuntu@<PUBLIC_IP_ADDRESS>
```

## 5. Deploy Aplikasi

### 5.1. Update Sistem
```bash
sudo apt update && sudo apt upgrade -y
```

### 5.2. Install Git dan Python
```bash
# Install Git
sudo apt install git -y

# Install Python 3 dan pip
sudo apt install python3 python3-pip python3-venv -y
```

### 5.3. Clone Repository
```bash
# Clone repository Anda (ganti dengan URL repository Anda)
git clone https://github.com/[username]/[repo-name].git forecast-vibecoding
cd forecast-vibecoding
```

### 5.4. Setup Virtual Environment
```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 5.5. Install Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Install gunicorn untuk production
pip install gunicorn
```

### 5.6. Jalankan Aplikasi
```bash
# Aktifkan virtual environment
source venv/bin/activate

# Pindah ke folder views
cd src/views

# Jalankan aplikasi
python app.py
```

## 6. Setup Production Deployment

### 6.1. Install dan Konfigurasi Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Kembali ke root folder
cd ~/forecast-vibecoding

# Test gunicorn
gunicorn --bind 0.0.0.0:8050 src.views.app:app.server
```

### 6.2. Setup Systemd Service
```bash
# Buat file service
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
ExecStart=/home/ubuntu/forecast-vibecoding/venv/bin/gunicorn --bind 0.0.0.0:8050 --workers 1 src.views.app:app.server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6.3. Aktifkan Service
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

## 7. Setup Scheduled Training

### 7.1. Buat Service untuk Scheduler
```bash
# Buat file service scheduler
sudo nano /etc/systemd/system/model-scheduler.service
```

Tambahkan konten berikut:
```ini
[Unit]
Description=Model Training Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/forecast-vibecoding
Environment=PATH=/home/ubuntu/forecast-vibecoding/venv/bin
ExecStart=/home/ubuntu/forecast-vibecoding/venv/bin/python src/services/scheduler_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7.2. Aktifkan Service Scheduler
```bash
# Reload daemon
sudo systemctl daemon-reload

# Mulai service
sudo systemctl start model-scheduler

# Aktifkan auto-start saat boot
sudo systemctl enable model-scheduler

# Cek status
sudo systemctl status model-scheduler
```

## 8. Akses Aplikasi

Aplikasi Anda sekarang bisa diakses melalui:
- http://<PUBLIC_IP_ADDRESS>:8050

## 9. Monitoring dan Troubleshooting

### 9.1. Cek Status Service
```bash
# Cek status aplikasi
sudo systemctl status dash-app

# Cek status scheduler
sudo systemctl status model-scheduler
```

### 9.2. Lihat Log
```bash
# Lihat log aplikasi
sudo journalctl -u dash-app -f

# Lihat log scheduler
sudo journalctl -u model-scheduler -f
```

## 10. Optimasi Biaya

### 10.1. Gunakan Spot Instance (Opsional)
- Spot instance lebih murah tapi bisa di-terminate
- Cocok untuk development dan testing

### 10.2. Monitor Penggunaan
- Gunakan Alibaba Cloud Monitor untuk melihat penggunaan resource
- Upgrade hanya jika diperlukan

## 11. Backup dan Recovery

### 11.1. Backup Manual
```bash
# Backup data penting
tar -czf backup-$(date +%Y%m%d).tar.gz mlruns/ models/
```

### 11.2. Gunakan Snapshot
- Gunakan fitur snapshot ECS untuk backup instance

## Troubleshooting Umum

### Aplikasi Tidak Bisa Diakses
1. Cek security group rules
2. Pastikan aplikasi bind ke 0.0.0.0 bukan 127.0.0.1
3. Cek firewall di instance: `sudo ufw status`

### RAM User Tidak Bisa Akses
1. Hubungi administrator RAM untuk memberikan izin ECS
2. Pastikan role yang diberikan cukup untuk operasi yang dibutuhkan

### Memory Penuh
1. Monitor penggunaan: `htop`
2. Restart service jika perlu: `sudo systemctl restart dash-app`

---

Catatan Penting:
- Simpan credential dan API key dengan aman
- Gunakan environment variables untuk konfigurasi sensitif
- Monitor penggunaan resource untuk mengoptimalkan biaya
- Backup data secara berkala