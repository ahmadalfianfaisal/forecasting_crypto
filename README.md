# Forecast Vibecoding

Aplikasi forecasting harga cryptocurrency menggunakan model Prophet dengan interface web berbasis Dash.

## Deskripsi

Aplikasi ini menyediakan platform forecasting harga cryptocurrency (terutama Big 3: BTC, ETH, SOL) menggunakan model Prophet. Aplikasi ini menyediakan antarmuka web yang memungkinkan pengguna untuk:
- Melihat grafik harga historis
- Melakukan forecasting untuk berbagai periode waktu (7D, 30D, 90D, 180D)
- Melihat metrik-metrik penting seperti volatilitas dan perubahan persentase
- Menjalankan pelatihan model secara otomatis

## Fitur

- Dashboard web real-time dengan grafik interaktif
- Forecasting harga cryptocurrency menggunakan model Prophet
- Penanganan nilai negatif dalam forecasting
- Sistem pelatihan model otomatis
- Support untuk Big 3 cryptocurrency (BTC, ETH, SOL)
- Desain antarmuka mirip Bloomberg

## Instalasi

1. Clone repository ini:
   ```bash
   git clone <repository-url>
   cd forecast-vibecoding
   ```

2. Buat virtual environment:
   ```bash
   python -m venv venv
   ```

3. Aktifkan virtual environment:
   ```bash
   # Di Windows
   venv\Scripts\activate
   
   # Di macOS/Linux
   source venv/bin/activate
   ```

4. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```

## Menjalankan Aplikasi

### Development Mode
1. Aktifkan virtual environment:
   ```bash
   # Di Windows
   venv\Scripts\activate
   
   # Di macOS/Linux
   source venv/bin/activate
   ```

2. Jalankan aplikasi:
   ```bash
   python run_app.py
   ```

3. Buka browser dan akses `http://127.0.0.1:8050`

### Local Mode (Recommended for local use)
Untuk menjalankan aplikasi dan scheduler secara lokal di komputer Anda:

1. Setup awal:
   ```cmd
   setup_windows.bat
   ```

2. Jalankan aplikasi dan scheduler bersamaan:
   ```cmd
   start_both_apps.bat
   ```

3. Akses aplikasi di `http://localhost:8050`

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
├── config/
├── tests/                        # File-file unit test
├── docs/                         # Dokumentasi
├── run_app.py                    # Entry point utama
├── run_scheduler.py              # Entry point scheduler
├── setup_windows.bat             # Script setup awal Windows
├── start_both_apps.bat           # Script start app dan scheduler
├── start_local_tmux_sessions.bat # Script untuk start tmux sessions (dengan WSL)
├── start_local_jobs.ps1          # Script untuk PowerShell jobs
├── LOCAL_TMUX_GUIDE.md           # Panduan jalankan lokal
├── requirements.txt              # Dependensi
└── README.md                     # Dokumentasi utama
```

## Local Deployment (Recommended for local use)

### Jalankan secara lokal di Windows
Ikuti panduan di `LOCAL_TMUX_GUIDE.md` untuk menjalankan aplikasi secara lokal dengan scheduled training.

## Penanganan Nilai Negatif

Aplikasi ini menyertakan fungsi `clip_negative_forecast()` untuk menangani kasus di mana model Prophet menghasilkan nilai negatif untuk harga cryptocurrency, yang tidak masuk akal secara logika bisnis.

## Scheduled Training

Aplikasi ini menyertakan sistem pelatihan model otomatis yang berjalan secara berkala untuk menjaga model tetap terbaru dengan data terkini. Scheduler berjalan secara terpisah dan dapat dikelola bersamaan dengan aplikasi utama.

## Teknologi yang Digunakan

- Python 3.8+
- Dash (Plotly)
- Prophet (Facebook)
- Pandas
- NumPy
- yfinance
- MLflow

## Kontribusi

Silakan fork repository ini dan submit pull request untuk kontribusi.

## Lisensi

[MIT License]