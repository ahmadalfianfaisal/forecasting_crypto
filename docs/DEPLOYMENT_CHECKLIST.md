# Informasi Deployment Penting

## Struktur File yang Dibutuhkan
Saat Anda upload kode ke instance ECS, pastikan Anda memiliki semua file berikut:

### File Utama:
- app.py (aplikasi Dash Anda)
- wsgi.py (entry point untuk Gunicorn)
- requirements.txt (daftar dependensi)
- gunicorn_config.py (konfigurasi Gunicorn)

### Folder dan File Data:
- semua folder dan file yang dibutuhkan oleh aplikasi Anda
- folder model_storage (jika ada model tersimpan)
- folder mlruns (untuk MLflow)
- folder data (jika ada data historis)

### File Scheduler:
- scheduler_daemon.py (untuk scheduled training)
- model_scheduler.service (konfigurasi systemd)

## Checklist Sebelum Deploy:
- [ ] Pastikan semua dependensi tercantum di requirements.txt
- [ ] Pastikan aplikasi berjalan lancar di lokal Anda
- [ ] Pastikan tidak ada credential sensitif di kode (gunakan environment variable)
- [ ] Backup data penting sebelum deployment

## Hak Akses yang Dibutuhkan:
Pastikan akun RAM Anda memiliki hak akses berikut:
- ECS: FullAccess atau minimal ability untuk:
  - Create/Manage instances
  - Manage security groups
  - View instances
- VPC: Access untuk mengelola jaringan
- SLB (Server Load Balancer): Jika Anda ingin menggunakan load balancer

## Estimasi Biaya Bulanan (untuk konfigurasi paling rendah):
- ECS ecs.s6-c1m1.large (1 vCPU, 1 GiB): ~Rp 100,000-150,000/bulan
- 40 GiB SSD Disk: ~Rp 20,000-30,000/bulan
- Traffic keluar: Gratis 10GB/bulan, setelah itu ~Rp 800/GB
- Total estimasi: ~Rp 150,000-200,000/bulan

## Tips untuk Hemat Biaya:
- Gunakan instance spot jika aplikasi Anda toleran terhadap interupsi
- Matikan instance saat tidak digunakan (jika hanya untuk testing)
- Monitor penggunaan resource dan upgrade hanya jika diperlukan

## Troubleshooting Umum:
1. Aplikasi tidak bisa diakses dari luar:
   - Cek security group rules
   - Pastikan firewall di instance tidak memblokir
   - Pastikan aplikasi bind ke 0.0.0.0 bukan 127.0.0.1

2. Memory penuh:
   - Monitor penggunaan memory
   - Pertimbangkan upgrade ke instance dengan RAM lebih besar

3. Scheduled training tidak jalan:
   - Cek status service: sudo systemctl status model_scheduler
   - Cek log: sudo journalctl -u model_scheduler -f

## Update Aplikasi Setelah Deploy:
Jika Anda perlu update aplikasi setelah deploy:
1. Lakukan perubahan di lokal
2. Upload file yang diubah ke instance
3. Restart service: sudo systemctl restart dash-app
4. Restart scheduler jika ada perubahan: sudo systemctl restart model_scheduler

## Backup dan Recovery:
- Backup database/model secara berkala
- Gunakan snapshot ECS untuk backup instance
- Simpan credential dan konfigurasi penting di tempat aman