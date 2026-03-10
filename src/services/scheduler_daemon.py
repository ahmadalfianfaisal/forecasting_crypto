"""
Scheduler untuk menjaga model tetap terlatih
"""
import schedule
import time
import logging
from datetime import datetime
from src.models.model_trainer import train_all_models
from src.utils.data_loader import get_available_tickers

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_training():
    """Fungsi untuk menjalankan pelatihan model"""
    try:
        logger.info("Memulai pelatihan model...")
        
        # Dapatkan daftar ticker yang tersedia
        tickers = [item['value'] for item in get_available_tickers()]
        logger.info(f"Ticker yang akan dilatih: {tickers}")
        
        # Latih semua model
        results = train_all_models(use_expanding_window=True)
        
        # Log hasil
        for ticker, success in results.items():
            status = "BERHASIL" if success else "GAGAL"
            logger.info(f"Pelatihan {ticker}: {status}")
        
        logger.info("Pelatihan model selesai.")
        
    except Exception as e:
        logger.error(f"Error saat menjalankan pelatihan: {str(e)}")

def main():
    """Fungsi utama scheduler"""
    logger.info("Scheduler dimulai...")
    
    # Jadwalkan pelatihan harian
    schedule.every().day.at("02:00").do(run_training)  # Jam 02:00 setiap hari
    
    # Untuk debugging, bisa tambahkan jadwal setiap jam
    # schedule.every().hour.do(run_training)
    
    # Jalankan pelatihan pertama kali
    logger.info("Menjalankan pelatihan pertama kali...")
    run_training()
    
    # Loop scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Cek setiap menit

if __name__ == "__main__":
    main()