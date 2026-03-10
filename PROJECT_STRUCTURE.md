# Struktur Folder Aplikasi Forecast Vibecoding

## Struktur Direktori yang Direkomendasikan

forecast-vibecoding/
├── src/
│   ├── __init__.py
│   ├── views/
│   │   ├── __init__.py
│   │   └── app.py                    # File utama Dash
│   ├── models/
│   │   ├── __init__.py
│   │   ├── forecast_model.py         # Model forecasting
│   │   ├── model_trainer.py          # Pelatihan model
│   │   ├── model_evaluation.py       # Evaluasi model
│   │   ├── model_storage.py          # Penyimpanan model
│   │   └── expanding_window_trainer.py # Pelatihan dengan window mengembang
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_loader.py            # Loader data
│   │   └── metrics.py                # Metrik evaluasi
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scheduler.py              # Scheduler utama
│   │   └── scheduler_daemon.py       # Daemon scheduler
│   └── controllers/
│       ├── __init__.py
│       └── (file-file controller lainnya)
├── config/
│   ├── __init__.py
│   ├── gunicorn_config.py           # Konfigurasi Gunicorn
│   ├── wsgi.py                     # Entry point WSGI
│   └── model_scheduler.service     # Konfigurasi systemd
├── tests/
│   ├── __init__.py
│   ├── test_forecast.py            # Test forecasting
│   ├── test_expanding_window.py    # Test window mengembang
│   ├── test_negative_handling.py   # Test penanganan negatif
│   └── simple_test_expanding_window.py
├── docs/
│   ├── DEPLOY_TO_ALIBABA_CLOUD.md  # Dokumentasi deployment
│   └── DEPLOYMENT_CHECKLIST.md     # Checklist deployment
├── models/                         # Folder penyimpanan model (dari kode)
├── mlruns/                         # Folder MLflow (dari kode)
├── __pycache__/                    # Cache Python (dari kode)
├── requirements.txt                # Dependensi
├── environment.yml                 # Environment Conda (jika ada)
├── mlflow.db                       # Database MLflow (jika ada)
├── 2.10.0                          # File versi (jika ada)
├── 5.0.0                           # File versi (jika ada)
└── README.md                       # Dokumentasi utama

## Perubahan yang Diperlukan pada File Import

### 1. app.py
Ubah semua import dari:
```python
from forecast_model import ...
from model_trainer import ...
from data_loader import ...
```

Menjadi:
```python
from src.models.forecast_model import ...
from src.models.model_trainer import ...
from src.utils.data_loader import ...
```

### 2. File-file lainnya
Sesuaikan import statements di semua file sesuai dengan struktur folder baru.

## File requirements.txt (sudah diperbarui)
dash>=2.14.0
dash-bootstrap-components>=1.5.0
dash-table>=5.0.0
plotly>=5.18.0
prophet>=1.1.5
yfinance>=0.2.36
pandas>=2.1.0
numpy>=1.26.0
APScheduler>=3.10.0
mlflow>=2.10.0
gunicorn>=21.2.0
schedule>=1.2.0

## File wsgi.py (untuk deployment)
```python
from src.views.app import app

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
```

## File gunicorn_config.py
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

## File model_scheduler.service
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

## File scheduler_daemon.py
Sesuaikan path import sesuai struktur folder baru.

## README.md (contoh)
```markdown
# Forecast Vibecoding

Aplikasi forecasting harga cryptocurrency menggunakan model Prophet.

## Instalasi

1. Clone repository
2. Buat virtual environment: `python -m venv venv`
3. Aktifkan virtual environment
4. Install dependensi: `pip install -r requirements.txt`

## Menjalankan Aplikasi

```bash
cd src/views
python app.py
```

Atau untuk deployment:
```bash
gunicorn --config ../config/gunicorn_config.py wsgi:server
```

## Struktur Proyek

- `src/views/app.py` - Aplikasi Dash utama
- `src/models/` - File-file model machine learning
- `src/utils/` - Fungsi-fungsi utilitas
- `src/services/` - Layanan background seperti scheduler
- `config/` - File-file konfigurasi
- `tests/` - File-file unit test
```

## Catatan Penting

1. Pastikan semua import path diupdate sesuai struktur folder baru
2. Test aplikasi setelah perubahan struktur folder
3. Backup sebelum merubah struktur folder yang ada
4. Gunakan virtual environment untuk development