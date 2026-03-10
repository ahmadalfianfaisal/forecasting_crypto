"""
Main entry point untuk aplikasi Forecast Vibecoding
Gunakan file ini untuk menjalankan aplikasi dari root direktori
"""

import sys
import os

# Tambahkan folder src ke path Python agar import bisa bekerja
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main function untuk menjalankan aplikasi"""
    # Import dan jalankan aplikasi
    from src.views.app import app
    
    print("Starting Forecast Vibecoding application...")
    print("Access the application at: http://0.0.0.0:8050")
    
    app.run(host="0.0.0.0", port=8050, debug=False)

if __name__ == "__main__":
    main()