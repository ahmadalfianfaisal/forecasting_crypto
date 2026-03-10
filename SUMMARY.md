# Ringkasan Proyek: Forecast Vibecoding

## Deskripsi Proyek
Aplikasi forecasting harga cryptocurrency menggunakan model Prophet dengan antarmuka web berbasis Dash. Aplikasi ini menyediakan forecasting untuk Big 3 cryptocurrency (BTC, ETH, SOL) dengan berbagai horizon waktu.

## Fitur Utama
1. **Dashboard Web Interaktif** - Antarmuka berbasis Dash dengan tampilan mirip Bloomberg
2. **Forecasting Harga** - Menggunakan model Prophet untuk memprediksi harga cryptocurrency
3. **Penanganan Nilai Negatif** - Fungsi untuk mencegah hasil forecasting negatif yang tidak masuk akal
4. **Scheduled Training** - Sistem pelatihan model otomatis untuk menjaga model tetap terbaru
5. **Big 3 Cryptocurrency Support** - Mendukung BTC, ETH, dan SOL

## Struktur Proyek
```
forecast-vibecoding/
├── src/
│   ├── views/
│   │   └── app.py                 # Aplikasi Dash utama
│   ├── models/
│   │   ├── forecast_model.py      # Model forecasting
│   │   ├── model_trainer.py       # Pelatihan model
│   │   ├── model_evaluation.py    # Evaluasi model
│   │   ├── model_storage.py       # Penyimpanan model
│   │   └── expanding_window_trainer.py # Pelatihan window mengembang
│   ├── utils/
│   │   ├── data_loader.py         # Loader data
│   │   └── metrics.py             # Metrik evaluasi
│   └── services/
│       ├── scheduler.py           # Scheduler utama
│       └── scheduler_daemon.py    # Daemon scheduler
├── config/                        # File konfigurasi
├── tests/                         # File test
├── docs/                          # Dokumentasi
├── run_app.py                     # Entry point utama
├── requirements.txt               # Dependensi
└── README.md                      # Dokumentasi utama
```

## Teknologi yang Digunakan
- **Python 3.8+**
- **Dash** - Framework web untuk antarmuka
- **Prophet** - Library forecasting dari Facebook
- **Pandas/Numpy** - Manipulasi data
- **yfinance** - Pengambil data keuangan
- **MLflow** - Tracking eksperimen dan model
- **Gunicorn** - Web server untuk deployment
- **Schedule** - Penjadwalan tugas otomatis

## Penanganan Nilai Negatif
Aplikasi ini menyertakan fungsi `clip_negative_forecast()` yang:
- Mencegah hasil forecasting negatif untuk harga cryptocurrency
- Mengganti nilai negatif dengan nilai positif minimal yang masuk akal
- Menjaga hubungan logis antara upper dan lower bounds

## Deployment ke Alibaba Cloud
Aplikasi siap untuk deployment ke Alibaba Cloud ECS dengan:
- Struktur folder yang terorganisir
- File konfigurasi untuk production
- Systemd service untuk menjaga aplikasi tetap berjalan
- Scheduled training untuk menjaga model tetap terbaru

## File Dokumentasi Tambahan
- `RAM_USER_DEPLOY_GUIDE.md` - Panduan deploy menggunakan RAM user
- `RAM_USER_PERMISSIONS.md` - Informasi tentang hak akses RAM
- `DEPLOYMENT_CHECKLIST_FINAL.md` - Checklist untuk deployment
- `PROJECT_STRUCTURE.md` - Detail struktur proyek

## Langkah-Langkah Selanjutnya
1. **Verifikasi RAM User Permissions** - Pastikan RAM user memiliki izin ECS
2. **Deploy ke Alibaba Cloud ECS** - Ikuti panduan deployment
3. **Setup Production Environment** - Konfigurasi service dan scheduler
4. **Monitor dan Maintain** - Pantau aplikasi dan lakukan pemeliharaan rutin

## Catatan Penting
- Aplikasi ini dirancang untuk berjalan 24/7 di server cloud
- Scheduled training akan menjaga model tetap terbaru dengan data terkini
- Penanganan nilai negatif memastikan hasil forecasting tetap realistis
- Struktur proyek yang rapi memudahkan pengembangan dan pemeliharaan di masa depan

---

Proyek ini siap untuk deployment production dan dapat diakses secara publik setelah deployment ke Alibaba Cloud.