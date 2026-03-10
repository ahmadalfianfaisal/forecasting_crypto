"""
Main entry point untuk scheduler model
Gunakan file ini untuk menjalankan scheduler dari root direktori
"""

import sys
import os

# Tambahkan folder src ke path Python agar import bisa bekerja
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main function untuk menjalankan scheduler"""
    # Import dan jalankan scheduler
    from src.services.scheduler_daemon import main as scheduler_main
    
    print("Starting Model Training Scheduler...")
    print("Scheduler is running in the background...")
    
    scheduler_main()

if __name__ == "__main__":
    main()